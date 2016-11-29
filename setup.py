#!/usr/bin/env python
"""Distutils setup for formatflowed.py"""

# Copyright (C) 2005-2012 Martijn Pieters
# Written by Martijn Pieters <mj@zopatista.com>
# Development was sponsored by Logicalware (http://www.logicalware.org/)
# Licensed as Open Source under the same terms as the Python 2.4.1 license,
# as available at http://www.python.org/2.4.1/license.html

import os
from setuptools import setup


version = '2.0.1'

install_requires = [
    'setuptools',
]


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as f:
        return f.read()


setup(
    name='formatflowed',
    version=version,
    description='RFC 3676 format=flowed text processing',
    long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
    license='Python Software Foundation License',
    platforms='OS Independent',
    author='Martijn Pieters',
    author_email='mj@zopatista.com',
    url='http://pypi.python.org/pypi/formatflowed',
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Communications :: Email',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup'
    ],
    install_requires=install_requires,
    test_suite='formatflowed',
)
