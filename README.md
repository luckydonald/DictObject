# DictObject
[![Build Status](https://travis-ci.org/luckydonald/DictObject.svg?branch=master)](https://travis-ci.org/luckydonald/DictObject) [![Coverage Status](https://coveralls.io/repos/github/luckydonald/DictObject/badge.svg?branch=master)](https://coveralls.io/github/luckydonald/DictObject?branch=master) [![<current version>](https://img.shields.io/pypi/v/DictObject.svg) ![<downloads>](https://img.shields.io/pypi/dm/DictObject.svg)](https://pypi.python.org/pypi/DictObject)


`DictObject` is a subclass of `dict` adding attribute-style access.
```python
some_dict = { "key": "value" }
bunch = DictObject( some_dict )
```
You can access values either like a dict,
```python
bunch["key"]  # 'value'
```
or object oriented attribute-style access:
```python
bunch.key  # 'value'
```
Both ways are possible, and the other always reflect the changes
```python
bunch.key = "something"
bunch["key"]  # 'something'
```

### Creating a `DictObject`
You can just drop a normal `dict` into it.
```python
a = DictObject({"I": "have", "no": "idea", "what": {"example": "names"}, "to": "choose"})
# you can chack equality as usual:
a == {"I": "have", "no": "idea", "what": {"example": "names"}, "to": "choose"}  # True
```
It's possibly to give a set set of keyword arguments.
```python
b = DictObject(test="foo", hurr="durr", best_pony = "Littlepip")
b == {"test": "foo", "hurr": "durr", "best_pony": "Littlepip"}  # True
```
You can merge multible `dict`s at once.
```python
a = {"one": 1, "two": 2, "three": 3}
b = {"eins": 1, "zwei": 2, "drei": 3}
c = DictObject(a, b)
c == {"one": 1, "two": 2, "three": 3, "eins": 1, "zwei": 2, "drei": 3}  # True
```
This works with everything subclassing 'dict', so you can use `DictObject` too.


Let's combine everything above:
```python
d = DictObject(c, unos=1, dos=2, tres=3)
d =={"one": 1, "two": 2, "three": 3, "eins": 1, "zwei": 2, "drei": 3, "unos": 1, "dos": 2, "tres": 3,}  # True
```
And you can define more values anytime by just setting them, per key or attribute
```python
e = DictObject()
e["isa"]    = 1
e["dalawa"] = 2
e["tatlo"]  = 3
e.ien = 1
e.twa  = 2
e.trije = 3
e == {"isa":1,"dalawa": 2,"tatlo": 3,"ien": 1,"twa": 2, "trije": 3}  # True
```
Have a look the `merge_dict` function in the code (it is documented there) how to merge another `dict` into a `DictObject`.
When a `list` is added to the `DictObject`, any `dict`s inside the list should become `DictObject`s too.
In order to archive that, `list`s are transformed to `DictObjectList`s.
It will still behave like normal lists, but added values will be automatically objectified.

This and more is found documentation in the code:    
[`DictObject/__init__.py`](https://github.com/luckydonald/DictObject/blob/master/DictObject/__init__.py)    
*(time of writing is [commit c41476e](https://github.com/luckydonald/DictObject/blob/68d8478721de2c8092fa5c407f39a1709c625d1f/DictObject/__init__.py#L45-L156))*

## Install
```sh
pip install DictObject
```

## Testing
For testing [doctest](https://docs.python.org/2/library/doctest.html)s where used, the documentation in the code doubles as testing.
Just run `test.py` or your prefered doctest engine.
