"""RFC 3676 format=flowed text processing.

This module provides an API to create and display text/plain; format=flowed 
mimetype text.

"""

# Copyright (C) 2005 Martijn Pieters
# Written by Martijn Pieters <mj@zopatista.com>
# Development was sponsored by Logicalware (http://www.logicalware.org/)
# Licensed as Open Source under the same terms as the Python 2.4.1 license,
# as available at http://www.python.org/2.4.1/license.html

__revision_id__ = '$Id$'

__all__ = ['FormatFlowedDecoder']

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
        encoding, using the default error handing scheme. 
        
    """
    def __init__(self, delete_space=False, character_set='us-ascii'):
        self.delete_space = delete_space
        self.character_set = character_set
        
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
            One of 'paragraph', 'fixed', 'signature-separator'
          quotedepth
            Number of quotemarks found on the text chunk
            
        chunk is a unicode string. All text is unwrapped and without any 
        quotemarks; when displaying these chunks, the appropriate quotemarks
        should be added again, and chunks of type 'paragraph' should be
        displayed wrapped. Chunks of type 'fixed' should be displayed 
        unwrapped.
        
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
            ...   ({'quotedepth': 2, 'type': 'paragraph'}, 
            ...     u"`Take some more tea,' the March Hare said to Alice, "
            ...     u"very earnestly."),
            ...   ({'quotedepth': 1, 'type': 'fixed'}, u""),
            ...   ({'quotedepth': 1, 'type': 'paragraph'}, 
            ...    u"`I've had nothing yet,' Alice replied in an offended "
            ...    u"tone, `so I can't take more.'"),
            ...   ({'quotedepth': 0, 'type': 'fixed'}, u""),
            ...   ({'quotedepth': 0, 'type': 'paragraph'}, 
            ...    u"`You mean you can't take less,' said the Hatter: `it's "
            ...    u"very easy to take more than nothing.'"),
            ...   ({'quotedepth': 0, 'type': 'fixed'}, u""),
            ...   ({'quotedepth': 0, 'type': 'signature-separator'}, u"-- "),
            ...   ({'quotedepth': 0, 'type': 'fixed'}, u"Lewis Carroll")
            ... ]
            True
        
        The decoder can deal with various cases of improperly format=flowed
        messages. Paragraphs normally end with a fixed line, but the following
        cases are also considered paragraph-closing cases:
        
        - A change in quotedepth:
        
            >>> result = decoder.decode(CRLF.join((
            ... "> Depth one paragraph with flow space. ",
            ... ">> Depth two paragraph with flow space. ",
            ... "Depth zero paragraph with fixed line.")))
            >>> list(result) == [
            ...   ({'quotedepth': 1, 'type': 'paragraph'},
            ...    u"Depth one paragraph with flow space. "),
            ...   ({'quotedepth': 2, 'type': 'paragraph'},
            ...    u"Depth two paragraph with flow space. "),
            ...   ({'quotedepth': 0, 'type': 'fixed'},
            ...    u"Depth zero paragraph with fixed line.")]
            True
        
        - A signature separator:
        
            >>> result = decoder.decode(CRLF.join((
            ... "A paragraph with flow space. ",
            ... "-- ")))
            >>> list(result) == [
            ...   ({'quotedepth': 0, 'type': 'paragraph'},
            ...    u"A paragraph with flow space. "),
            ...   ({'quotedepth': 0, 'type': 'signature-separator'}, u"-- ")]
            True
            
        - The end of the message:
        
            >>> result = decoder.decode(CRLF.join((
            ... "A paragraph with flow space. ",)))
            >>> list(result) == [
            ...   ({'quotedepth': 0, 'type': 'paragraph'},
            ...    u"A paragraph with flow space. ")]
            True
            
        The delete_space attribute of the FormatFlowedDecoder class can be used
        to control wether or not the trailing space on flowed lines should be
        retained; this is used to encode flowed text where spaces are rare:
        
            >>> decoder = FormatFlowedDecoder(delete_space=True)
            >>> result = decoder.decode(CRLF.join((
            ... "Contrived example with a word- ",
            ... "break across the paragraph.")))
            >>> list(result) == [
            ...   ({'quotedepth': 0, 'type': 'paragraph'}, 
            ...    u'Contrived example with a word-break across the '
            ...    u'paragraph.')]
            True
        
        """
        para = u''
        pinfo = {'type': 'paragraph'}
        for line in flowed.decode(self.character_set).split('\r\n'):
            quotedepth, line = self._stripquotes(line)
            line = self._stripstuffing(line)
            if line == '-- ':
                # signature separator
                if para:
                    # exception case: flowed line followed by sig-sep
                    yield (pinfo, para)
                    pinfo = {'type': 'paragraph'}
                    para = u''
                yield ({'type': 'signature-separator', 
                        'quotedepth': quotedepth}, line)
                continue
            if line.endswith(u' '):
                # flowed line; collect into a paragraph
                if quotedepth != pinfo.get('quotedepth', quotedepth):
                    # exception case: flowed line followed by quotedepth change
                    yield (pinfo, para)
                    pinfo = {'type': 'paragraph'}
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
                    pinfo = {'type': 'paragraph'}
                    para = u''
                else:
                    yield (pinfo, para + line)
                    pinfo = {'type': 'paragraph'}
                    para = u''
                    continue
            yield ({'type': 'fixed', 'quotedepth': quotedepth}, line)
            
        if para:
            # exception case: last line was a flowed line
            yield (pinfo, para)
            

def _test(verbose=False):
    import doctest
    return doctest.testmod(verbose=verbose)

if __name__ == '__main__':
    import sys
    _test('-v' in sys.argv)
