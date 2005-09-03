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


def _test(verbose=False):
    import doctest
    return doctest.testmod(verbose=verbose)

if __name__ == '__main__':
    import sys
    _test('-v' in sys.argv)
