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
    version='0.9.0',
    description='RFC 3676 format=flowed text processing',
    author='Martijn Pieters',
    author_email='mj@zopatista.com',
    url='http://www.zopatista.com/projects/formatflowed',
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