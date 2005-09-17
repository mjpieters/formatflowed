#!/usr/bin/env python
"""Distutils setup for formatflowed.py"""

# Copyright (C) 2005 Martijn Pieters
# Written by Martijn Pieters <mj@zopatista.com>
# Development was sponsored by Logicalware (http://www.logicalware.org/)
# Licensed as Open Source under the same terms as the Python 2.4.1 license,
# as available at http://www.python.org/2.4.1/license.html

__revision_id__ = '$Id$'


from distutils.core import setup

setup(
    name='formatflowed',
    version='1.0.0',
    description='RFC 3676 format=flowed text processing',
    long_description='''\
The formatflowed.py python library provides en- and decoding functionality for 
`RFC 2646`_ and `RFC 3676`_ text, also called format=flowed text. The 
development of this library was generously sponsored by `Logicalware`_.

.. _RFC 2646: http://www.faqs.org/rfcs/rfc2646.html
.. _RFC 3676: http://www.faqs.org/rfcs/rfc3676.html
.. _Logicalware: http://www.logicalware.com/''',
    license='Python Software Foundation License',
    platforms='OS Independent',
    author='Martijn Pieters',
    author_email='mj@zopatista.com',
    url='http://www.zopatista.com/projects/formatflowed',
    download_url='http://www.zopatista.com/projects/formatflowed/'
                 'releases/1.0.0/formatflowed-1.0.0.tar.gz',
    keywords=('email', 'mime', 'format', 'flowed', 'rfc2646', 'rfc3676'),
    py_modules=['formatflowed'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup'
    ]
)