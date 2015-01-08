__author__ = 'luckydonald'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
def test():
	import DictObject
	import doctest
	returned = doctest.testmod(DictObject)
	return returned.failed

if __name__ == '__main__':
	sys.exit(test())