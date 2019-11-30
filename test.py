# -*- coding: utf-8 -*-
import sys
__author__ = 'luckydonald'

def test():
    import DictObject
    import DictObject.autosave
    DictObject.______do_more_doctests______()  # for coverage report.
    import doctest
    returned = []
    returned.append(doctest.testmod(DictObject, verbose=True))
    returned.append(doctest.testmod(DictObject.autosave, verbose=True))
    return all(returned)


if __name__ == '__main__':
    sys.exit(test())
