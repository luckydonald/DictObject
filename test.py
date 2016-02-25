# -*- coding: utf-8 -*-
import sys
__author__ = 'luckydonald'

def test():
    import DictObject
    import doctest
    returned = doctest.testmod(DictObject, verbose=True)
    return returned.failed


if __name__ == '__main__':
    sys.exit(test())
