# -*- coding: utf-8 -*-
import sys
__author__ = 'luckydonald'

def test():
    import DictObject
    DictObject.______do_more_doctests______()  # for coverage report.
    import doctest
    returned = doctest.testmod(DictObject, verbose=True)
    return returned.failed


if __name__ == '__main__':
    sys.exit(test())
