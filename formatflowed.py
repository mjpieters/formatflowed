"""RFC 3676 format=flowed text processing.

This module provides an API to create and display text/plain; format=flowed 
mimetype text.

"""

# Copyright (C) 2005-2012 Martijn Pieters
# Written by Martijn Pieters <mj@zopatista.com>
# Development was sponsored by Logicalware (http://www.logicalware.org/)
# Licensed as Open Source under the same terms as the Python 2.4.1 license,
# as available at http://www.python.org/2.4.1/license.html


import re
import textwrap

__all__ = [
    'PARAGRAPH',
    'FIXED',
    'SIGNATURE_SEPARATOR',
    'FormatFlowedDecoder', 
    'FormatFlowedEncoder',
    'decode',
    'encode',
    'convertToWrapped',
    'convertToFlowed'
]

# Constants denoting the various text chunk types recognized by format=flowed
PARAGRAPH, FIXED, SIGNATURE_SEPARATOR = range(3)


# -- Public classes ----------------------------------------------------


class FormatFlowedDecoder:
    """Object for converting format=flowed text to other formats
    
    The following instance attributes influence the interpretation of
    format=flowed text:
      delete_space (default: False)
        Delete the trailing space before the CRLF on flowed lines before 
        interpreting the line on flowed input, corresponds to the DelSp mime
        parameter
      character_set (default: us-ascii)
        The encoding of text passed in. Text is decoded to unicode using this
        encoding, using the error handling scheme specified below. 
      error_handling (default: strict)
        The error handling scheme used when decoding the text.
        
    """
    def __init__(self, delete_space=False, character_set='us-ascii',
                 error_handling='strict'):
        self.delete_space = delete_space
        self.character_set = character_set
        self.error_handling = error_handling
        
    # -- Private methods -----------------------------------------------
    
    def _stripquotes(self, line):
        """Remove quotemarks from the start of the line
        
        Returns the number of quotemarks stripped and the stripped line:
        
            >>> decoder = FormatFlowedDecoder()
            >>> decoder._stripquotes(u'>>> quoted line')
            (3, u' quoted line')
        
        Non-quoted lines are returned unchanged:
        
            >>> decoder._stripquotes(u'non-quoted line')
            (0, u'non-quoted line')
        
        """
        stripped = line.lstrip('>')
        return len(line) - len(stripped), stripped
    
    def _stripstuffing(self, line):
        """Remove the optional leading space
        
        Returns the stripped line:
        
            >>> decoder = FormatFlowedDecoder()
            >>> decoder._stripstuffing(u' stuffed line')
            u'stuffed line'
        
        Non-stuffed lines are returned unchanged:
        
            >>> decoder._stripstuffing(u'non-stuffed line')
            u'non-stuffed line'
        
        Additional spacing is preserved:
        
            >>> decoder._stripstuffing(u'  extra leading space')
            u' extra leading space'
        
        """
        if line.startswith(u' '):
            return line[1:]
        return line
    
    def _stripflow(self, line):
        """Remove the trailing flow space is delete_space is set
        
        The instance attribute delete_space is False by default thus this
        method returns the line unchanged:
        
            >>> decoder = FormatFlowedDecoder()
            >>> decoder._stripflow(u'flowed line ')
            u'flowed line '
        
        But if the delete_space attribute has been set to True the flow space
        is removed:
        
            >>> decoder = FormatFlowedDecoder(delete_space=True)
            >>> decoder._stripflow(u'flowed line ')
            u'flowed line'
        
        Only one flow space is removed:
        >>> decoder._stripflow(u'extra whitespace  ')
        u'extra whitespace '
        
        """
        if self.delete_space and line.endswith(u' '):
            return line[:-1]
        return line
    
    # -- Public API ----------------------------------------------------
        
    def decode(self, flowed):
        """Decode flowed text
        
        Returns an iterable serving a sequence of (information, chunk)
        tuples. information is a dictionary with the following fields:
          type
            One of PARAGRAPH, FIXED, SIGNATURE_SEPARATOR
          quotedepth
            Number of quotemarks found on the text chunk
            
        chunk is a unicode string. All text is unwrapped and without any 
        quotemarks; when displaying these chunks, the appropriate quotemarks
        should be added again, and chunks of type PARAGRAPH should be
        displayed wrapped. Chunks of type FIXED should be displayed 
        unwrapped.
        
        
        Examples
        --------
        
        Here is a simple example:
        
            >>> CRLF = '\\r\\n'
            >>> decoder = FormatFlowedDecoder()
            >>> result = decoder.decode(CRLF.join((
            ... ">> `Take some more tea,' the March Hare said to Alice, very ",
            ... ">> earnestly.",
            ... ">",
            ... "> `I've had nothing yet,' Alice replied in an offended ",
            ... "> tone, `so I can't take more.'",
            ... "",
            ... "`You mean you can't take less,' said the Hatter: `it's very ",
            ... "easy to take more than nothing.'",
            ... "",
            ... "-- ",
            ... "Lewis Carroll")))
            >>> list(result) == [
            ...   ({'quotedepth': 2, 'type': PARAGRAPH}, 
            ...     u"`Take some more tea,' the March Hare said to Alice, "
            ...     u"very earnestly."),
            ...   ({'quotedepth': 1, 'type': FIXED}, u""),
            ...   ({'quotedepth': 1, 'type': PARAGRAPH}, 
            ...    u"`I've had nothing yet,' Alice replied in an offended "
            ...    u"tone, `so I can't take more.'"),
            ...   ({'quotedepth': 0, 'type': FIXED}, u""),
            ...   ({'quotedepth': 0, 'type': PARAGRAPH}, 
            ...    u"`You mean you can't take less,' said the Hatter: `it's "
            ...    u"very easy to take more than nothing.'"),
            ...   ({'quotedepth': 0, 'type': FIXED}, u""),
            ...   ({'quotedepth': 0, 'type': SIGNATURE_SEPARATOR}, u"-- "),
            ...   ({'quotedepth': 0, 'type': FIXED}, u"Lewis Carroll")
            ... ]
            True
        
            
        Improperly closed paragraphs
        ----------------------------
        
        The decoder can deal with various cases of improperly format=flowed
        messages. Paragraphs normally end with a fixed line, but the following
        cases are also considered paragraph-closing cases:
        
        - A change in quotedepth:
        
            >>> result = decoder.decode(CRLF.join((
            ... "> Depth one paragraph with flow space. ",
            ... ">> Depth two paragraph with flow space. ",
            ... "Depth zero paragraph with fixed line.")))
            >>> list(result) == [
            ...   ({'quotedepth': 1, 'type': PARAGRAPH},
            ...    u"Depth one paragraph with flow space. "),
            ...   ({'quotedepth': 2, 'type': PARAGRAPH},
            ...    u"Depth two paragraph with flow space. "),
            ...   ({'quotedepth': 0, 'type': FIXED},
            ...    u"Depth zero paragraph with fixed line.")]
            True
        
        - A signature separator:
        
            >>> result = decoder.decode(CRLF.join((
            ... "A paragraph with flow space. ",
            ... "-- ")))
            >>> list(result) == [
            ...   ({'quotedepth': 0, 'type': PARAGRAPH},
            ...    u"A paragraph with flow space. "),
            ...   ({'quotedepth': 0, 'type': SIGNATURE_SEPARATOR}, u"-- ")]
            True
            
        - The end of the message:
        
            >>> result = decoder.decode(CRLF.join((
            ... "A paragraph with flow space. ",)))
            >>> list(result) == [
            ...   ({'quotedepth': 0, 'type': PARAGRAPH},
            ...    u"A paragraph with flow space. ")]
            True
            
            
        Decoder options
        ---------------
            
        The delete_space attribute of the FormatFlowedDecoder class can be used
        to control wether or not the trailing space on flowed lines should be
        retained; this is used to encode flowed text where spaces are rare:
        
            >>> decoder = FormatFlowedDecoder(delete_space=True)
            >>> result = decoder.decode(CRLF.join((
            ... "Contrived example with a word- ",
            ... "break across the paragraph.")))
            >>> list(result) == [
            ...   ({'quotedepth': 0, 'type': PARAGRAPH}, 
            ...    u'Contrived example with a word-break across the '
            ...    u'paragraph.')]
            True
            
        Note that the characterset determines what how to interpret a space
        and a quote marker. The cp037 characterset does not encode these 
        characters the same way, for example:
        
            >>> decoder = FormatFlowedDecoder(character_set='cp037')
            >>> result = decoder.decode(CRLF.join((
            ... "n@\\xe3\\x88\\x89\\xa2@\\x89\\xa2@\\x81@\\x98\\xa4\\x96\\xa3"
            ... "\\x85\\x84@\\x97\\x81\\x99\\x81\\x87\\x99\\x81\\x97\\x88@",
            ... "n@\\x85\\x95\\x83\\x96\\x84\\x85\\x84@\\x89\\x95@\\x83\\x97"
            ... "\\xf0\\xf3\\xf7K")))
            >>> list(result) == [
            ...   ({'quotedepth': 1, 'type': PARAGRAPH},
            ...    u'This is a quoted paragraph encoded in cp037.')]
            True
            
        """
        para = u''
        pinfo = {'type': PARAGRAPH}
        for line in flowed.split('\r\n'):
            line = line.decode(self.character_set, self.error_handling)
            quotedepth, line = self._stripquotes(line)
            line = self._stripstuffing(line)
            if line == '-- ':
                # signature separator
                if para:
                    # exception case: flowed line followed by sig-sep
                    yield (pinfo, para)
                    pinfo = {'type': PARAGRAPH}
                    para = u''
                yield ({'type': SIGNATURE_SEPARATOR, 
                        'quotedepth': quotedepth}, line)
                continue
            if line.endswith(u' '):
                # flowed line; collect into a paragraph
                if quotedepth != pinfo.get('quotedepth', quotedepth):
                    # exception case: flowed line followed by quotedepth change
                    yield (pinfo, para)
                    pinfo = {'type': PARAGRAPH}
                    para = u''
                para += self._stripflow(line)
                pinfo['quotedepth'] = quotedepth
                continue
            # fixed line
            if para:
                # completed paragraph
                if quotedepth != pinfo.get('quotedepth', quotedepth):
                    # exception case: flowed line followed by quotedepth change
                    yield (pinfo, para)
                    pinfo = {'type': PARAGRAPH}
                    para = u''
                else:
                    yield (pinfo, para + line)
                    pinfo = {'type': PARAGRAPH}
                    para = u''
                    continue
            yield ({'type': FIXED, 'quotedepth': quotedepth}, line)
            
        if para:
            # exception case: last line was a flowed line
            yield (pinfo, para)


class FormatFlowedEncoder:
    """Object to generate format=flowed text
    
    The following attributes influence the flowed formatting of text:
      extra_space (default: False)
        Use an extra space to create flowed lines; this requires that the
        DelSpace flag will be set true on the Content-Type mime header. Use
        this flag on texts that have little or no spaces to break on.
      character_set (default: us-ascii)
        Encode the output to this character set.
      error_handling (default: strict)
        The error handling scheme used when encoding the text.
        
      spacestuff_quoted (default: True)
        Always spacestuff quoted chunks, i.e. place a space between the quote
        markers and the text.
      width (default: 78)
        The maximum line width generated for flowed paragraphs; fixed lines
        can still exceed this width. This value does not include the CRLF
        line endings.
        
    """
    def __init__(self, extra_space=False, character_set='us-ascii',
                 error_handling='strict', spacestuff_quoted=True, width=78):
        self.extra_space = extra_space
        self.character_set = character_set
        self.error_handling = error_handling
        self.spacestuff_quoted = spacestuff_quoted
        self.width = width
        
    def _spacestuff(self, line, force=False):
        """Prepend a space to lines starting with ' ', '>' or 'From'
        
        Returns the altered line. Set 'force' to True to skip the tests and
        always prepend the space regardless:
        
            >>> encoder = FormatFlowedEncoder()
            >>> encoder._spacestuff(u' leading space needs to be preserved')
            u'  leading space needs to be preserved'
            >>> encoder._spacestuff(u'> can be confused for a quotemark')
            u' > can be confused for a quotemark'
            >>> encoder._spacestuff(u'From is often escaped by MTAs')
            u' From is often escaped by MTAs'
            >>> encoder._spacestuff(u'Padding is considered harmless')
            u'Padding is considered harmless'
            >>> encoder._spacestuff(u'So forcing it is fine', True)
            u' So forcing it is fine'
            
        Note that empty lines can never be spacestuffed:
        
            >>> encoder._spacestuff(u'')
            u''
            
        """
        if not line:
            return line
        # Although the RFC doesn't say so explicitly, in practice 'From' only
        # needs escaping when (1) not quoted and (2) actually encoded as
        # 'From' (so independent of the unicode sequence u'From').
        # For simplicity's sake, we spacestuff it any time a line starts with 
        # it before adding quotemarks and encoding the line.
        if force or line[0] in (' ', '>') or line.startswith('From'):
            return u' ' + line
        return line
        
    # -- Public API ----------------------------------------------------
    
    def encode(self, chunks):
        """Encode chunks of text to format=flowed
        
        chunks
          An iterable sequence of (information, text) tuples, where information
          is a dictionary with 'type' and 'quotedepth' keys. The 'type' value
          is one of PARAGRAPH, FIXED or SIGNATURE-SEPARATOR, and the
          'quotedepth' value a positive integer indicating the quoting depth.
          text should be the unicode text to be encoded.
          
        Example
        -------
        
        To illustrate, an example:
        
            >>> chunks = (
            ...   ({'quotedepth': 2, 'type': PARAGRAPH}, 
            ...     u"`Take some more tea,' the March Hare said to Alice, "
            ...     u"very earnestly."),
            ...   ({'quotedepth': 1, 'type': FIXED}, u""),
            ...   ({'quotedepth': 1, 'type': PARAGRAPH}, 
            ...    u"`I've had nothing yet,' Alice replied in an offended "
            ...    u"tone, `so I can't take more.'"),
            ...   ({'quotedepth': 0, 'type': FIXED}, u""),
            ...   ({'quotedepth': 0, 'type': PARAGRAPH}, 
            ...    u"`You mean you can't take less,' said the Hatter: `it's "
            ...    u"very easy to take more than nothing.'"),
            ...   ({'quotedepth': 0, 'type': FIXED}, u""),
            ...   ({'quotedepth': 0, 'type': SIGNATURE_SEPARATOR}, u"-- "),
            ...   ({'quotedepth': 0, 'type': PARAGRAPH}, u"Carol Lewis"),
            ... )
            >>> result = FormatFlowedEncoder(width=45).encode(chunks)
            >>> result.split('\\r\\n') == [
            ...   ">> `Take some more tea,' the March Hare said ",
            ...   ">> to Alice, very earnestly.",
            ...   ">",
            ...   "> `I've had nothing yet,' Alice replied in ",
            ...   "> an offended tone, `so I can't take more.'",
            ...   "",
            ...   "`You mean you can't take less,' said the ",
            ...   "Hatter: `it's very easy to take more than ",
            ...   "nothing.'",
            ...   "",
            ...   "-- ",
            ...   "Carol Lewis",
            ...   ""]
            True

        """
        encoded = []
        for info, text in chunks:
            encoded.append(self.encodeChunk(text, **info))
        return ''.join(encoded)
    
    def encodeChunk(self, chunk, type=PARAGRAPH, quotedepth=0):
        """Encode a chunk of text to format=flowed
        
        The chunk is encoded to format=flowed text, controlled by the 
        following arguments.
        chunk
          The unicode text to be encoded. Newlines are considered to be
          whitespace and will be converted to spaces.
        type (default: PARAGRAPH)
          Chunk type; one of PARAGRAPH, FIXED or SIGNATURE_SEPARATOR. When
          called with type SIGNATURE_SEPARATOR the chunk is ignored and '-- '
          is written out.
        quotedepth (default: 0)
          The quote depth of the chunk.
          
          
        Examples
        --------
          
        The encoder has to deal with three types of text chunks. To illustrate,
        we create a encoder instance geared:
        
            >>> encoder = FormatFlowedEncoder(width=45)
            
        We can then use this encoder to encode some examples of these different
        types:
            
        - fixed lines:
        
            >>> encoder.encodeChunk(u'A fixed line remains unaltered', FIXED)
            'A fixed line remains unaltered\\r\\n'
            >>> encoder.encodeChunk(u'Although quoting is prepended', FIXED, 2)
            '>> Although quoting is prepended\\r\\n'
            >>> encoder.encodeChunk(u'Trailing spaces are removed  ', FIXED)
            'Trailing spaces are removed\\r\\n'
            >>> encoder.encodeChunk(u'> and special first chars are fluffed',
            ...                     FIXED)
            ' > and special first chars are fluffed\\r\\n'
            
        - a paragraph (the default type):
        
            >>> result = encoder.encodeChunk(
            ...   u"`Take some more tea,' the March Hare said to Alice, "
            ...   u"very earnestly.")
            >>> result == ("`Take some more tea,' the March Hare said \\r\\n"
            ...            "to Alice, very earnestly.\\r\\n")
            True
            >>> result = encoder.encodeChunk(
            ...   u"`I've had nothing yet,' Alice replied in an offended "
            ...   u"tone, `so I can't take more.'", PARAGRAPH, 1)
            >>> result == ("> `I've had nothing yet,' Alice replied in \\r\\n"
            ...            "> an offended tone, `so I can't take more.'\\r\\n")
            True
            >>> result = encoder.encodeChunk(
            ...   u'The   wrapping   deals   quite   well  with > eratic '
            ...   u'spacing and space fluffs characters where needed.')
            >>> result == ("The   wrapping   deals   quite   well  with \\r\\n"
            ...            " > eratic spacing and space fluffs \\r\\n"
            ...            "characters where needed.\\r\\n")
            True
        
        - signature separators:
        
            >>> encoder.encodeChunk(u'-- ', SIGNATURE_SEPARATOR)
            '-- \\r\\n'
            >>> encoder.encodeChunk(u'-- ', SIGNATURE_SEPARATOR, 3)
            '>>> -- \\r\\n'
            
          Note that the actual chunk value is ignored for this type:
        
            >>> encoder.encodeChunk(u'foobar', SIGNATURE_SEPARATOR)
            '-- \\r\\n'
            
            
        Encoder options
        ---------------
            
        The encoding can be influenced by several instance attributes; the
        width attribute was used for the paragraph demonstrations. Others
        include 'extra_space', 'character_set' and 'spacestuff_quoted':
        
        - extra_space generates extra spaces on flowed lines so flowed lines
          can be broken on something other than whitespace:
          
            >>> encoder = FormatFlowedEncoder(extra_space=True, width=45)
            >>> result = encoder.encodeChunk(
            ...   u'This is useful for texts with many word-breaks or few '
            ...   u'spaces')
            >>> result == ("This is useful for texts with many word- \\r\\n"
            ...            "breaks or few spaces\\r\\n")
            True
            
        - character_set controls the output encoding:
        
            >>> encoder = FormatFlowedEncoder(character_set='cp037')
            >>> result = encoder.encodeChunk(u'Can you read me now?',
            ...                              quotedepth=1)
            >>> result == ('n@\\xc3\\x81\\x95@\\xa8\\x96\\xa4@\\x99\\x85\\x81'
            ...            '\\x84@\\x94\\x85@\\x95\x96\\xa6o\\r\\n')
            True
            
        - spacestuff_quoted causes quoted lines to be spacestuffed by default;
          this makes for slightly more readable quoted text output. It is on
          by default, but can be switched off:
          
            >>> encoder = FormatFlowedEncoder(spacestuff_quoted=False)
            >>> encoder.encodeChunk(u'Look Ma! No space!', quotedepth=1)
            '>Look Ma! No space!\\r\\n'
            
            
        RFC 2822 compliance
        -------------------
        
        Note that RFC 2822 requires that generated lines never exceed the
        hard limit of 998 characters without the CRLF at the end. The encoder 
        has to enforce this by chopping the lines up into pieces not exceeding
        that length:
        
            >>> encoder = FormatFlowedEncoder()
            >>> result = encoder.encodeChunk(u'-' * 1500, FIXED)
            >>> result = result.split('\\r\\n')
            >>> len(result)
            3
            >>> len(result[0])
            998
            >>> result == ['-' * 998, '-' * 502, '']
            True
            
        """
        # cleanup: replace newlines with spaces and remove trailing spaces
        chunk = ' '.join(chunk.rstrip().splitlines())
        
        # Pre-encode quoting
        quotemarker = u'>' * quotedepth
        quotemarker = quotemarker.encode(self.character_set)
        forcestuff = self.spacestuff_quoted and quotedepth > 0

        if type == SIGNATURE_SEPARATOR:
            chunk = u'-- '
            
        if type == PARAGRAPH:
            # Maximum width is reduced by stuffing and quotemarkers
            width = self.width - len(quotemarker) - 2
            if width <= 0:
                raise ValueError('Not enough width for both quoting and text')
            wrapper = _FlowedTextWrapper(width, self.extra_space)
            chunk = wrapper.wrap(chunk)
        else:
            chunk = [chunk]
        
        lines = []
        for line in chunk:
            # add space to flowed lines (all but last); this is an extra space
            # if the wrapping of paragraphs included spaces at the end of the
            # lines.
            if line != chunk[-1]:
                line += ' '
            line = self._spacestuff(line, forcestuff)
            line = quotemarker + line.encode(self.character_set,
                                             self.error_handling)
            
            # Enforce a hard limit of 998 characters per line (excluding CRLF)
            # Unfortunately we can only enforce this *after* encoding,
            # otherwise we could flow lines that are too long.
            while len(line) > 998:
                lines.append(line[:998])
                line = line[998:]
                
            lines.append(line)
            
        lines.append('') # ensure last ending CRLF
        return '\r\n'.join(lines)
    
    
# -- Convenience functions ---------------------------------------------


def decode(flowed, **kwargs):
    """Convert format=flowed text
    
    See the FormatFlowedDecoder.decode docstring for more information. All
    keyword arguments are passed to the FormatFlowedDecoder instance.
    
    """
    decoder = FormatFlowedDecoder(**kwargs)
    return decoder.decode(flowed)

def encode(chunks, **kwargs):
    """Convert chunks of text to format=flowed
    
    See the FormatFlowedEncoder.encode docstring for more information. All
    keyword arguments are passed to the FormatFlowedEncoder instance.
    
    """
    encoder = FormatFlowedEncoder(**kwargs)
    return encoder.encode(chunks)

def convertToWrapped(flowed, width=78, quote=u'>', wrap_fixed=True, **kwargs):
    """Covert flowed text to encoded and wrapped text
    
    Create text suitable for a proportional font, fixed with, plain text
    display. The argements are interpreted as follows:
      flowed
        The format=flowed formatted text to convert
      width (default: 78)
        The maximum line length at which to wrap paragraphs. 
      quote (default: u'>')
        Character sequence to use to mark quote depths; it is multiplied with
        the quotedepth to quote a line. If this sequence does not end in a
        space a space is added between the quotemars and the line.
      wrap_fixed (default: True)
        If true, fixed text chunks are wrapped to the given  width as well,
        including hard word breaks if a word exceeds the line width
        
      The remaining arguments are used as arguments to FormatFlowedDecoder.
      
      Here is a simple example:
    
        >>> CRLF = '\\r\\n'
        >>> result = convertToWrapped(CRLF.join((
        ... ">> `Take some more tea,' the March Hare said to Alice, very ",
        ... ">> earnestly.",
        ... ">",
        ... "> `I've had nothing yet,' Alice replied in an offended ",
        ... "> tone, `so I can't take more.'",
        ... "",
        ... "`You mean you can't take less,' said the Hatter: `it's very ",
        ... "easy to take more than nothing.'",
        ... "",
        ... "-- ",
        ... "Lewis Caroll")), width=60)
        >>> result.split('\\n') == [
        ...   ">> `Take some more tea,' the March Hare said to Alice, very",
        ...   ">> earnestly.", 
        ...   "> ",
        ...   "> `I've had nothing yet,' Alice replied in an offended tone,",
        ...   "> `so I can't take more.'",
        ...   "",
        ...   "`You mean you can't take less,' said the Hatter: `it's very",
        ...   "easy to take more than nothing.'",
        ...   "",
        ...   "-- ",
        ...   "Lewis Caroll"]
        True
        
    """
    result = []
    for info, chunk in decode(flowed, **kwargs):
        type = info['type']
        quotedepth = info['quotedepth']
        quotemarker = quotedepth and quote * quotedepth or u''
        if quotemarker and quote[-1] != u' ':
            quotemarker += u' '
        if type == FIXED and not wrap_fixed:
            result.append(quotemarker + chunk)
        elif not chunk or type == SIGNATURE_SEPARATOR:
            result.append(quotemarker + chunk)
        else:
            result.extend(textwrap.wrap(chunk, width,
                                        replace_whitespace=False,
                                        initial_indent=quotemarker,
                                        subsequent_indent=quotemarker))
    return u'\n'.join(result)

def convertToFlowed(text, quotechars=u'>|%', **kwargs):
    """Convert plain text to format=flowed
    
    Attempt to interpret the plain text as paragraphs and fixed lines, 
    creating a format=flowed encoded text. The paragraph detection is fairly 
    simple and probably not suitable for real-world email.
    
    text
      Unicode text to be converted. Paragraphs are detected based on
      whitelines between them, making all lines with extra linespace at the
      start fixed to preserve that whitespace.
    quotechars (default: u'>|%')
      A set of characters recognized as quote markers; used to detect quote
      depth.
    
    Additional kwargs are passed on to FormatFlowedEncoder.
    
    """
    encoder = FormatFlowedEncoder(**kwargs)
    return encoder.encode(_parseFlowableChunks(text, quotechars))
    
    
# -- Private classes and methods ---------------------------------------


class _FlowedTextWrapper(textwrap.TextWrapper):
    """Custom text wrapper for flowed text
    
    When not using extra spaces, only break on spaces; when we are using
    extra spaces, don't swallow whitespace at the start and end of lines, but
    do break long words (as they can be reconstructed with DelSpace on).
    
    """
    def __init__(self, width=78, extra_space=False):
        textwrap.TextWrapper.__init__(self, width,
                                      break_long_words=extra_space)
        self.extra_space = extra_space
        if not extra_space:
            self.wordsep_re = re.compile(r'(\s+)')
            
    def _handle_long_word(self, reversed_chunks, cur_line, cur_len, width):
        # _handle_long_word taken from python 2.5 CVS speed optimisation
        # Can be removed if this is used with python 2.5
        space_left = max(width - cur_len, 1)
        if self.break_long_words:
            cur_line.append(reversed_chunks[-1][:space_left])
            reversed_chunks[-1] = reversed_chunks[-1][space_left:]
        elif not cur_line:
            cur_line.append(reversed_chunks.pop())
        
    def _wrap(self, chunks):
        # Simplified and customized version of textwrap.TextWrapper
        # Based on textwrapper rev. 1.37 in python CVS, with speed optimisation
        lines = []
        chunks.reverse()
        while chunks:
            cur_line = []
            cur_len = 0
            width = self.width

            # Don't strip space at the start of a line when using extra_space
            # because spaces are significant there.
            if chunks[-1].strip() == '' and lines and not self.extra_space:
                del chunks[-1]

            while chunks:
                l = len(chunks[-1])
                if cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l
                else:
                    break

            if chunks and len(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)

            # Don't drop space at end of line if using extra_space for
            # marking flowed lines because otherwise there is no space between
            # this line and the next when decoding the flowed text
            if cur_line and cur_line[-1].strip() == '' and not self.extra_space:
                del cur_line[-1]

            if cur_line:
                lines.append(''.join(cur_line))
        return lines
    

def _parseFlowableChunks(text, quotechars='>%|'):
    """Parse out encodeble chunks, determining chunk type
    
    First step is to remove and count quoting marks, determining the quotedepth
    of the text. Then the type of the lines is detected.
    
    Paragraphs are determined by terminating lines; terminating lines are
    changes in quoting (depth or quoting used, signatures or fixed lines (see 
    below)
    
    Fixed lines are used for lines with nothing but whitespace and for lines 
    with whitespace prepended (indented lines).
    
    Any line with only two dashes at the start and whitespace is a signature
    seperator.
    
    Example code:
    
        >>> result = _parseFlowableChunks(u'\\n'.join((
        ...     u'Normal text, as long as they are not delimited by empty ',
        ...     u'lines will be considered paragraphs and will be parsed as ',
        ...     u'such.',
        ...     u'',
        ...     u'> > Quoting will be detected as well, and as long as it is ',
        ...     u'> > consistent text will be collected into one paragraph.',
        ...     u'> Changes in depth trigger a new paragraph.',
        ...     u'>      Leading whitespace makes for fixed lines.',
        ...     u'Signature separators are dealt with accordingly:',
        ...     u'-- '
        ... )))
        >>> result.next() == ({'type': PARAGRAPH, 'quotedepth': 0},
        ...     u'Normal text, as long as they are not delimited by empty '
        ...     u'lines will be considered paragraphs and will be parsed as '
        ...     u'such.')
        True
        >>> result.next() == ({'type': FIXED, 'quotedepth': 0}, u'')
        True
        >>> result.next() == ({'type': PARAGRAPH, 'quotedepth': 2},
        ...     u'Quoting will be detected as well, and as long as it is '
        ...     u'consistent text will be collected into one paragraph.')
        True
        >>> result.next() == ({'type': PARAGRAPH, 'quotedepth': 1},
        ...     u'Changes in depth trigger a new paragraph.')
        True
        >>> result.next() == ({'type': FIXED, 'quotedepth': 1},
        ...     u'     Leading whitespace makes for fixed lines.')
        True
        >>> result.next() == ({'type': PARAGRAPH, 'quotedepth': 0},
        ...     u'Signature separators are dealt with accordingly:')
        True
        >>> result.next() == ({'type': SIGNATURE_SEPARATOR, 'quotedepth': 0},
        ...     u'-- ')
        True
        >>> result.next()
        Traceback (most recent call last):
            ...
        StopIteration
        
    """
    # Match quotemarks with limited whitespace around them
    qm_match = re.compile('(^\s{0,2}([%s]\s?)+)' % quotechars).match
    # Find all quotemarks
    qm_findall = re.compile('[%s]' % quotechars).findall
    
    quotedepth = 0
    quotemarks = ''
    para = u''
    
    for line in text.splitlines():
        has_quotes = qm_match(line)
        same_quotes = quotemarks and line.startswith(quotemarks)
        if (has_quotes and not same_quotes) or (not has_quotes and quotedepth):
            # Change in quoting
            if para:
                yield {'type': PARAGRAPH, 'quotedepth': quotedepth}, para
                para = u''
            
            quotemarks = has_quotes and has_quotes.group(0) or u''
            quotedepth = len(qm_findall(quotemarks))
            
        line = line[len(quotemarks):]
        
        if line.rstrip() == u'--':
            # signature separator
            if para:
                yield {'type': PARAGRAPH, 'quotedepth': quotedepth}, para
                para = u''
                
            yield {'type': SIGNATURE_SEPARATOR, 'quotedepth': quotedepth}, line
            continue
        
        if line.strip() == u'' or line.lstrip() != line:
            # Fixed line
            if para:
                yield {'type': PARAGRAPH, 'quotedepth': quotedepth}, para
                para = u''
                
            yield {'type': FIXED, 'quotedepth': quotedepth}, line
            continue
        
        # Paragraph line; store and loop to next line
        para += line
        
    if para:
        yield {'type': PARAGRAPH, 'quotedepth': quotedepth}, para
    
def additional_tests():
    # Run tests with python setup.py test (req. python 2.4)
    import doctest
    import sys
    return doctest.DocTestSuite(sys.modules[__name__])

def _test(verbose=False):
    import doctest
    return doctest.testmod(verbose=verbose)

if __name__ == '__main__':
    # Run tests with python formatflowed.py
    import sys
    _test('-v' in sys.argv)
