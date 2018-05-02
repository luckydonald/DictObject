import re
import sys

try:
    from collections.abc import MutableSequence, MutableSet  # python 3

except ImportError:
    from collections import MutableSequence, MutableSet  # py2

from luckydonaldUtils import encoding
from luckydonaldUtils.encoding import to_native as n
import logging

__all__ = ["DictObject", "DictObjectList"]
__author__ = 'luckydonald'
__version__ = '1.0.4'
logger = logging.getLogger(__name__)

unallowed_in_variable_name = re.compile('[\W]+')


def suppress_context(exc):
    exc.__context__ = None
    return exc


class SomeDict(dict):
    """
    Not sure what this class does. I forgot. Sorry. So now I am using it for setting up doctest.

    # To allow logger output to be checked:
    >>> logger.warning("Logger Successfully registered.")
    Logger Successfully registered.
    """
    pass
# end class


class SelfObjectifyMixin(object):
    """
    To provide the same functionality to both the list and the set implementations
    """
    @staticmethod
    def iterator_objectified(iterable):
        """
        You put in a generator, it will return objectified version of the values.

        Example:
            >>> input = [0, 1, {"foo": "bar"}, [True, False]]
            >>> iterator = SelfObjectifyMixin.iterator_objectified(input)
            >>> result = [x for x in iterator]

            >>> result
            [0, 1, {'foo': 'bar'}, [True, False]]
            >>> type(result[2])
            <class 'DictObject.DictObject'>
            >>> type(result[3])
            <class 'DictObject.DictObjectList'>

            It also accepts DictObject and DictObject itself:

            >>> input = [DictObject(test="successful"), DictObjectList([1, 2, 3])]
            >>> iterator = DictObjectList.iterator_objectified(input)
            >>> result = [x for x in iterator]

            >>> result
            [{'test': 'successful'}, [1, 2, 3]]
            >>> type(result[0])
            <class 'DictObject.DictObject'>
            >>> type(result[1])
            <class 'DictObject.DictObjectList'>

        :param iterable: something to iterate on
        :return: a new iterable, you can use instead
        """
        for i in iterable:
            yield DictObject.objectify(i)
        # end for
    # end def
# end class


class DictObjectList(list, MutableSequence, SelfObjectifyMixin):
    """
    List which wraps the builtin list, to automatically objectify any dicts/sets in this list.

    Examples:
    >>> d = {"foo": "bar"}
    >>> l = ["hi", 1, True, None, d]

    >>> dict_l = DictObjectList(l)
    >>> dict_l == l
    True
    >>> isinstance(dict_l[4], DictObject)
    True

    >>> dict_l.append(d)
    >>> isinstance(dict_l[5], DictObject)
    True

    >>> d2 = {"yeah": "foo"}
    >>> dict_l.extend([d2, [1,2,3]])
    >>> isinstance(dict_l[6], DictObject)
    True
    >>> isinstance(dict_l[7], DictObjectList)
    True
    """

    def __init__(self, iterable=None):
        super(DictObjectList, self).__init__(DictObjectList.iterator_objectified(iterable))
    # end def __init__

    def insert(self, index, value):
        """
        Insert object before index.

        Example:
            >>> l = DictObjectList([1, 2, 3, 4])
            >>> l.insert(2, "middle")
            >>> l
            [1, 2, 'middle', 3, 4]

        :param index: Before which element we want to insert it
        :param value: The value to insert
        :return:
        """
        obj_value = DictObject.objectify(value)
        return super(DictObjectList, self).insert(index, obj_value)

    def __iadd__(self, values):
        obj_values = DictObject.objectify(values)
        return super(DictObjectList, self).__iadd__(obj_values)

    def extend(self, values):
        obj_value = DictObject.objectify(values)
        super(DictObjectList, self).extend(obj_value)

    def append(self, value):
        obj_value = DictObject.objectify(value)
        super(DictObjectList, self).append(obj_value)

    def __setitem__(self, index, value):
        """
       Set self[key] to value.

       Example:
           >>> l = DictObjectList([1, 2, 3])
           >>> l[1] = "middle"
           >>> l
           [1, 'middle', 3]

       :param index: Which item to replace
       :param value: The value to set
       :return:
       """
        obj_value = DictObject.objectify(value)
        return super(DictObjectList, self).__setitem__(index, obj_value)
    # end def
# end class


class DictObjectSet(set, MutableSet, SelfObjectifyMixin):
    """
    List which wraps the builtin set, to automatically objectify any dicts/lists in this set.

    Examples:
    >>> s = {"hi", 1, True, None}

    >>> dict_s = DictObjectSet(s)
    >>> dict_s == s
    True
    >>> dict_s.update([False, 1,2,3])
    >>> dict_s == {False, True, 2, 3, None, 'hi'}
    True
    """

    def __init__(self, iterable=None):
        super(DictObjectSet, self).__init__(DictObjectSet.iterator_objectified(iterable))
    # end def __init__

    def add(self, element):
        super().add(DictObject.objectify(element))
    # end def

    def update(self, *values):
        super().update(*DictObject.objectify(values))
    # end def
# end class


class DictObject(SomeDict):
    """
    DictObject is a subclass of dict with attribute-style access.

            >>> some_dict = { "key": "value" }
            >>> bunch = DictObject( some_dict )

        You can access values either like a dict,

            >>> bunch["key"]
            'value'

        Or object oriented attribute-style access

            >>> bunch.key
            'value'

        Both ways are possible, and the other always reflect the changes

            >>> bunch.key = "something"
            >>> bunch["key"]
            'something'


        --------------
         Setting data
        --------------

        You can just drop a dict into it.
            >>> a = DictObject({"I": "have", "no": "idea", "what": {"example": "names"}, "to": "choose"})

            >>> a == {"I": "have", "no": "idea", "what": {"example": "names"}, "to": "choose"}
            True

        It's possibly to give a set set of keyword arguments.

            >>> b = DictObject(test="foo", hurr="durr", best_pony="Littlepip")

            >>> b == {"test": "foo", "hurr": "durr", "best_pony": "Littlepip"}
            True

        You can merge multible dicts at once.

            >>> a = {"one": 1, "two": 2, "three": 3}
            >>> b = {"eins": 1, "zwei": 2, "drei": 3}
            >>> c = DictObject(a, b)
            >>> c == {"one": 1, "two": 2, "three": 3, "eins": 1, "zwei": 2, "drei": 3}
            True

        This works with everything subclassing 'dict', so you can use DictObject too.
        You also can combine everything above.


            >>> d = DictObject(c, unos=1, dos=2, tres=3)
            >>> d =={"one": 1, "two": 2, "three": 3, "eins": 1, "zwei": 2, "drei": 3, "unos": 1, "dos": 2, "tres": 3,}
            True

        And you can define more values anytime by just setting them, per key or attribute

            >>> e = DictObject()

            >>> e["isa"]    = 1
            >>> e["dalawa"] = 2
            >>> e["tatlo"]  = 3

            >>> e.ien = 1
            >>> e.twa  = 2
            >>> e.trije = 3

            >>> e == {"isa":1,"dalawa": 2,"tatlo": 3,"ien": 1,"twa": 2, "trije": 3}
            True

        See below (in the merge_dict function)
        how to merge another dict into a DictObject.

        When a list is added to the DictObject, any Dicts inside the list should become DictObjects too.
        In order to archive that, Lists are transformed to DictObjectList.
        It will still behave like normal lists, but added values will be automatically objectified.

            Some tests, not ideal as example:
            >>> e.test = []
            >>> e.test.append({"hey":"wow"})
            >>> e.test
            [{'hey': 'wow'}]
            >>> type( e.test )
            <class 'DictObject.DictObjectList'>
            >>> e.test[0]
            {'hey': 'wow'}
            >>> e.test[0]["hey"]
            'wow'
            >>> type( e.test[0] )
            <class 'DictObject.DictObject'>
            >>> e.test[0].hey
            'wow'
            >>> e.test.append({"huh":"wow"})
            >>> e.test == [{'hey': 'wow'}, {'huh': 'wow'}]
            True
            >>> e.test += [{'third': 'wow'}]
            >>> e.test[2]
            {'third': 'wow'}
            >>> type(e.test[2])
            <class 'DictObject.DictObject'>
            >>> e.test.extend([{'fourth': 'wow'}])
            >>> e.test == [{'hey': 'wow'}, {'huh': 'wow'}, {'third': 'wow'}, {'fourth': 'wow'}]
            True
            >>> type(e.test[3])
            <class 'DictObject.DictObject'>
            >>> f = DictObject.objectify(["a",])
            >>> f
            ['a']
            >>> type(f)
            <class 'DictObject.DictObjectList'>

            >>> g = {"tuple": (0, 1, {"dict": "yeah"}, ["list", "huuu"])}
            >>> g = DictObject.objectify(g)
            >>> type(g)
            <class 'DictObject.DictObject'>
            >>> g == {'tuple': (0, 1, {'dict': 'yeah'}, ['list', 'huuu'])}
            True
            >>> isinstance(g["tuple"], tuple)
            True
            >>> type(g.tuple[2])
            <class 'DictObject.DictObject'>
            >>> type(g.tuple[3])
            <class 'DictObject.DictObjectList'>

    """

    def __init__(self, *args, **kwargs):
        if len(args) == 1:
            dict.__init__(self, *args, **kwargs)
        else:
            dict.__init__(self, **kwargs)
        # end if
        self._attribute_to_key_map = {}  # else they will be still here if i instanciate a new one.
        """ 
        Resolves the attributes (properties) of this class instance to the original dict's attributes.
        So `dict.foo_2_4_` can be resolved as `dict["foo-: '.4;"]`.
        
        The key is the attribute name,
        the value is the full, original name used as original key.
        Examples:
            "int_1"    > "1"
            "foo_2_4_" > "foo-: '2.4;"
        """
        # process kwarg elements als key=value for this dict.
        kwargs_dict = dict(**kwargs)
        for arg in args:
            self.merge_dict(arg)
        self.merge_dict(kwargs_dict)

    @classmethod
    def objectify(cls, obj):
        if isinstance(obj, (DictObject, DictObjectList, DictObjectSet)):
            return obj
        elif isinstance(obj, list):  # add all list elements
            return DictObjectList(DictObject.objectify(x) for x in obj)
        elif isinstance(obj, set):
            return DictObjectSet(DictObject.objectify(x) for x in obj)
        elif isinstance(obj, tuple):
            return type(obj)(DictObject.objectify(x) for x in obj)
        elif isinstance(obj, dict):  # add dict recursivly
            return DictObject(obj)
        else:  # add single element
            return obj
        # end if
    # end def

    @classmethod
    def normalify(cls, obj):
        """
        Reverses the effect of DictObject.objectify().
        DictObject becomes a dict again, and DictObjectList becomes a list again.

            >>> i = {'int': 123, 'bool': True, 'null':None, 'string': "test", 'dict':{'waifu': 'littlepip'}, 'list': [1, 2, 3, {'TEST':'SUCCESS'}]}
            >>> o = DictObject.objectify(i)
            >>> o == i
            True
            >>> d = DictObject.normalify(o)
            >>> o == d
            True
            >>> isinstance(i, dict), isinstance(o, dict), isinstance(d, dict)
            (True, True, True)
            >>> isinstance(i, DictObject), isinstance(o, DictObject), isinstance(d, DictObject)
            (False, True, False)
            >>> isinstance(i['dict'], dict), isinstance(o['dict'], dict), isinstance(d['dict'], dict)
            (True, True, True)
            >>> isinstance(i['dict'], DictObject), isinstance(o['dict'], DictObject), isinstance(d['dict'], DictObject)
            (False, True, False)
            >>> isinstance(i['list'], list), isinstance(o['list'], list), isinstance(d['list'], list)
            (True, True, True)
            >>> isinstance(i['list'], DictObjectList), isinstance(o['list'], DictObjectList), isinstance(d['list'], DictObjectList)
            (False, True, False)
            >>> isinstance(i['list'][3], dict), isinstance(o['list'][3], dict), isinstance(d['list'][3], dict)
            (True, True, True)
            >>> isinstance(i['list'][3], DictObject), isinstance(o['list'][3], DictObject), isinstance(d['list'][3], DictObject)
            (False, True, False)


        :param obj:
        :return:
        """
        if isinstance(obj, DictObject):
            return DictObject.normalify(dict(obj))
        elif isinstance(obj, DictObjectList):
            return DictObject.normalify(list(obj))
        elif isinstance(obj, DictObjectSet):
            return DictObject.normalify(set(obj))
        elif isinstance(obj, (list, tuple, set,)):  # add all list-like elements
            return type(obj)(DictObject.normalify(x) for x in obj)
            # this is list(... for ... in ...) or set(... for ... in ...)
            # type(obj)( ... for ... in ..)   for e.g. list is same as   [( ... for ... in ..)]
        elif isinstance(obj, dict):  # add dict recursivly
            return {k: DictObject.normalify(v) for k, v in obj.items()}
        else:  # add single element
            return obj
        # end if
    # end def

    def merge_dict(self, d):
        """
        ---------------
         Merging dicts
        ---------------

        You know what is more fun than a dict?
        Adding more dict to it.

            >>> first_dict  = {"best pony":'Littlepip'}
            >>> second_dict = {"best fiction":"Fallout: Equestria"}

        There we got some Dicts. Let's merge!

            >>> a = DictObject( first_dict )
            >>> a.merge_dict( second_dict ) # doctest: +ELLIPSIS
            {...}

        but you can go all fancy and use the += operator:

            >>> a += {"4458":"just google it?"}


            >>> a == {'4458': 'just google it?', 'best fiction':'Fallout: Equestria', 'best pony': 'Littlepip'}
            True

        This will overwrite existing values.

            >>> other_test = DictObject( {"key":"original value"} )

            >>> other_test += {"key":"changed value"}

            >>> other_test["key"] == 'changed value'
            True

        TypeError will be raised, if the given element is not a dict:

            >>> other_test += 1234
            Traceback (most recent call last):
                ...
            TypeError: Argument is no dict.

        """
        if not isinstance(d, dict):
            raise TypeError("Argument is no dict.")
        # self._dict = d
        for a, b in d.items():
            attribute_name = self.get_attribute_name_by_key(a)
            self._add_to_object_part(a, b)
            self._attribute_to_key_map[n(attribute_name)] = a
        return self

    def __iadd__(self, other):
        self.merge_dict(other)
        return self

    @staticmethod
    def get_attribute_name_by_key(key):
        """
        To get a methods name from a key name.
        Methods only allow a-z, A-Z, _ and after the first charakter 0-9
        Continue reading below.

            >>> DictObject.get_attribute_name_by_key("test123-456.7")
            'test123_456_7'

            >>> b = DictObject()

        Keys starting with an Number will be prefixed with 'int_'

            >>> b[2] = "heya"
            >>> b[2]
            'heya'
            >>> b.int_2
            'heya'
            >>> b += { "1": "foo" }
            >>> b.int_1
            'foo'

            >>> b += {"2abc345": "foobar"}
            >>> b.int_2abc345
            'foobar'

        It allows you to use non string values, but they will be prefixed with 'data_', and the rest will be the result
        of str(key).

            >>> b[False] = 456
            >>> b[False]
            456
            >>> False in b
            True
            >>> b.data_False
            456

            >>> b[None] = 1234
            >>> b.data_None
            1234

        And finally illegal characters will be replaced with underscores, but adding only one singe underscore
        between legal characters. (nobody likes to count ______ underscores!)

            >>> b += { 'foo-2.4;"':'foo again' }
            >>> b.foo_2_4_
            'foo again'

            # just a check if everything got added to b so far:
            >>> b ==  {False: 456, 2: 'heya', None: 1234, '1': 'foo', 'foo-2.4;"': 'foo again', '2abc345': 'foobar'}
            True

        Now it is possible that 2 keys will be stripped to the same attribute string. To keep them accessable
         they will be numbered. To be more precisely, '_n' will be appended, with 'n' being the next free number.

            >>> del b
            >>> b = DictObject()

            >>> b["1"] = "a"
            >>> b
            {'1': 'a'}

            >>> # To allow logger output to be checked by the tests, you don't need that in your code.
            >>> import sys; logger.addHandler(logging.StreamHandler(sys.stdout))

            >>> b[1] =  "b"
            <BLANKLINE>
            CRITICAL WARNING in DictObject: Mapped key '1' to attribute 'int_1_1', because attribute 'int_1' was already set by key '1'.

            >>> b = DictObject()

            >>> b[1] = "a"
            >>> b
            {1: 'a'}

            >>> b['1'] =  "b"
            <BLANKLINE>
            CRITICAL WARNING in DictObject: Mapped key '1' to attribute 'int_1_1', because attribute 'int_1' was already set by key '1'.


        """

        attribute_name = str(key)
        if str(key)[0].isdigit():
            attribute_name = "int_" + str(attribute_name)
        # to access  a = {'1':'foo'}  with DictObject(a).int_1
        # Note:  a = {'2foo4u':'bar'} will be DictObject(a).int_2foo4u
        elif not isinstance(key, (str, encoding.native_type, encoding.unicode_type)):
            attribute_name = "data_" + str(attribute_name)
        # a[None] = 'foo'  >   a.data_None

        attribute_name = unallowed_in_variable_name.sub('_',
                                                        attribute_name)  # a = {'foo-2.4;"':'foo'} becomes DictObject(a).foo_2_4_
        return attribute_name

    def _add_to_object_part(self, name, obj):
        dict.__setitem__(self, name, DictObject.objectify(obj))
        return

    # Items (Array/Dict)

    # no __getitem__ because we want to use the dict's one.

    def __setitem__(self, key, value):
        """
        Updates the value, or creates a new item.

        >>> b = DictObject({"foo": {"lol": True}, "hello":42, "ponies":'are pretty!'})
        >>> b["foo"] = "updated value"
        >>> b == {'ponies': 'are pretty!', 'foo': 'updated value', 'hello': 42}
        True
        >>> b.foo
        'updated value'
        >>> b["foo"]
        'updated value'
        >>> b["bar"] = "created value"
        >>> b == {'ponies': 'are pretty!', 'foo': 'updated value', 'bar': 'created value', 'hello': 42}
        True
        >>> b["bar"]
        'created value'
        >>> b.bar
        'created value'
        >>> b.barz = "more created value"
        >>> b["barz"]
        'more created value'
        >>> b.barz
        'more created value'
        >>> b.barz = "changed this."
        >>> b["barz"]
        'changed this.'
        >>> b.barz
        'changed this.'
        """
        attribute_name = self.get_attribute_name_by_key(key)
        unique_attribute_name = attribute_name
        # check, if there is already a key representing this attribute
        if n(attribute_name) in self._attribute_to_key_map and self._attribute_to_key_map[n(attribute_name)] != key:
            # This attribute is already set, but the key is not.
            # Now search for the next free one
            i = 1
            while i != 0:
                unique_attribute_name = attribute_name + "_" + str(i)
                i = i + 1 if (n(unique_attribute_name) in self._attribute_to_key_map and
                              self._attribute_to_key_map[n(unique_attribute_name)] != key) else 0
            # if is not free name, continue to increase,
            # else, if is free, set to 0 to exit loop
            # end while
            logger.warn(
                "\nCRITICAL WARNING in DictObject: Mapped key '%s' to attribute '%s', "
                "because attribute '%s' was already set by key '%s'." % (
                    key, unique_attribute_name, attribute_name, self._attribute_to_key_map[n(attribute_name)]))
        value = self.on_set(key, value)
        self._add_to_object_part(key, value)
        self._attribute_to_key_map[n(unique_attribute_name)] = key
        self.after_set(key, value)

    def __delitem__(self, key):
        """
        Deletes an item by key.

        >>> b = DictObject({"test": "123", "littlepip": 'best pony!', 'something': 'else'})
        >>> del b["test"]
        >>> b == {'littlepip': 'best pony!', 'something': 'else'}
        True

        >>> del b.something
        >>> b == {'littlepip': 'best pony!'}
        True

        >>> b.clear()
        >>> b == {}
        True

        :param key: The key to delete.
        :return: Nothing.
        """
        if self.on_del(key):
            attribute_name = self.get_attribute_name_by_key(key)
            del self._attribute_to_key_map[n(attribute_name)]
            dict.__delitem__(self, key)
            self.after_del(key)

    # Attributes (Object)

    def __setattr__(self, name, value):
        if name.startswith("_"):
            # self._attribute_to_key_map = value
            super(DictObject, self).__setattr__(name, value)
            return
        else:
            key_name = self._attribute_to_key_map[n(name)] if n(
                name) in self._attribute_to_key_map else name  # if there is a key representing this attribute
        # update this key, too
        value = self.on_set(name, value)
        self._add_to_object_part(name, value)  # needed allways to keep items  beeing recursive.
        self._attribute_to_key_map[n(name)] = key_name  # needed only on adding new element. (not when updating)
        # object.__setattr__(self, key, value)
        dict.__setitem__(self, self._attribute_to_key_map[n(name)],
                         DictObject.objectify(value))  # self[self._key_map[key]] = value
        self.after_set(name, value)

    def __getattr__(self, name):
        """
        Directly pulls the content form the dict itself,
        works as long as _key_map is correct.

        >>> b = DictObject({"foo": {"lol": True}, "hello":42, "ponies":'are pretty!'})
        >>> b.notexist
        Traceback (most recent call last):
            ...
        AttributeError: notexist

        >>> b = DictObject()
        >>> b.notexist
        Traceback (most recent call last):
            ...
        AttributeError: notexist
        """
        _exception = None  # py2
        try:
            value = dict.__getattribute__(self,
                                          n(name))  # Raise exception if not found in original dict's attributes either
            return value
        except AttributeError:
            try:
                if n(name) in self.__dict__:
                    return self.__dict__[n(name)]
                if self._attribute_to_key_map:
                    key_name = self._attribute_to_key_map[n(name)]  # Check if we have this set.
                    self.on_get(key_name)
                    value = dict.__getitem__(self, key_name)  # self[key_name]
                    value = self.after_get(key_name, value)
                    return value
                else:
                    if not sys.version < '3':  # python 2.7
                        raise suppress_context(AttributeError(name))
                    # print("_attribute_to_key_map not defined.")
                    _exception = AttributeError(name)
                    _exception.__cause__ = None

            except KeyError:
                if not sys.version < '3':  # python 2.7
                    raise suppress_context(AttributeError(name))
                _exception = AttributeError(name)
                _exception.__cause__ = None
            finally:
                if _exception:
                    raise _exception
        finally:
            if _exception:
                raise _exception

    def __delattr__(self, name):
        """
        >>> b = DictObject({"foo": {"lol": True}, "hello":42, "ponies":'are pretty!'})
        >>> b._lol = "hey"
        >>> b._lol
        'hey'
        >>> b['_lol']
        Traceback (most recent call last):
            ...
        KeyError: '_lol'

        >>> del b._lol
        """
        # object.__delattr__(self, item)
        if name in self.__dict__:
            del self.__dict__[name]
        if n(name) in self._attribute_to_key_map:
            key = self._attribute_to_key_map[n(name)]
            if self.on_del(key):
                dict.__delitem__(self, key)
                del self._attribute_to_key_map[n(name)]
            self.after_del(key)

    def __contains__(self, k):
        """

            >>> b = DictObject(ponies='are pretty!')
            >>> 'ponies' in b
            True
            >>> 'foo' in b
            False
            >>> b['foo'] = 42
            >>> 'foo' in b
            True
            >>> b.hello = 'hai'
            >>> 'hello' in b
            True
            >>> b[None] = 123
            >>> None in b
            True
            >>> b[False] = 456
            >>> False in b
            True

        """
        try:
            return dict.__contains__(self, k) or hasattr(self, k)
        except:
            return False

    def on_get(self, key):
        """
        Override this to do modify data, on an easy way,
        without the need to fiddle with all the getter
        and setter methods yourself.

        This will be called with the key.  (from the dict, not the attribute)
        To get or modify the value, use after_get

        """
        pass

    def on_set(self, key, value_to_set):
        """
        Same idea as on_get()
        Override to get control about the content written.
        This function will be called before the content (value) reaches the dict,
        so you can modify it here.
        The value this function returns will be stored in the dict.
        """
        return value_to_set

    def on_del(self, key):
        """
        You got the idea. almost identical to on_get and on_set
        Just no value is given.
        This function allows you to prevent a entry from beeing deleted.
        If you don't return True, the value will not be deleted!

        YOU MUST RETURN TRUE TO DELETE!
        """
        return True

    def after_get(self, key, value):
        """
        This is to get or modify the value, use after_get

        Same as on_get, but is after retrieving the data get,
        so we now have a value too.

        What you will returned will be returned to the call.

        Example:
        Our object is called ``foo_object``.
        When requesting
        >> foo_object.bar
        this function will be called.
        If we return ``None`` here, it will result in
        >> foo_object.bar == None
        same goes for
        >> foo_object["bar"] == None

        """

        return value

    def after_set(self, key, value):
        """
        Same as on_set, but the value is already stored,
        and there is no need for returning anything
        """
        pass

    def after_del(self, key):
        """
        Same as on_del, but the key is already deleted.
        Please note, this function is not called, if on_del() returned a False
        and so aborted deletion.
        """
        pass

    def __reduce__(self):
        """
        Inherit dict's reduce, which don't work without explicitly calling it
        """  # https://stackoverflow.com/a/46560454/3423324
        return super().__reduce__()
    # end def

    def __getstate__(self):
        return self.__dict__
    # end def

    def __setstate__(self, d):
        #print(repr(d))
        # {'_attribute_to_key_map': {'some_key': 'some key'}}
        if isinstance(d, dict) and '_attribute_to_key_map' in d:
            self.__setattr__('_attribute_to_key_map', d['_attribute_to_key_map'])
            del d['_attribute_to_key_map']
        # end if
        self.__dict__.update(d)
    # end def


def ______do_more_doctests______():
    """
    For test suite, so we don't spam it in one of the classes.

        >>> e = {"a":{"b":{"c":{"d": "foo","e":"bar"}}}, "best pony":"Littlepip", "1":"should be 'int_1' as attribute", "foo-:-bar": "should be 'foo_bar' as attribute."}
        >>> b = DictObject(e)
        >>> b == {"a":{"b":{"c":{"d": "foo","e":"bar"}}}, "best pony":"Littlepip", "1":"should be 'int_1' as attribute", "foo-:-bar": "should be 'foo_bar' as attribute."}
        True
        >>> b.a == {'b': {'c': {'e': 'bar', 'd': 'foo'}}}
        True
        >>> b.a.c
        Traceback (most recent call last):
            ...
        AttributeError: c
        >>> b.a.b.c == {'e': 'bar', 'd': 'foo'}
        True
        >>> b.a["b"].c == {'e': 'bar', 'd': 'foo'}
        True
        >>> b.a["b"].c["e"] = "barz"
        >>> b == {'a': {'b': {'c': {'e': 'barz', 'd': 'foo'}}}, '1': "should be 'int_1' as attribute", 'foo-:-bar': "should be 'foo_bar' as attribute.", 'best pony': 'Littlepip'}
        True
        >>> b.a["b"].c.e = "barz2"
        >>> b == {'a': {'b': {'c': {'e': 'barz2', 'd': 'foo'}}}, '1': "should be 'int_1' as attribute", 'foo-:-bar': "should be 'foo_bar' as attribute.", 'best pony': 'Littlepip'}
        True
        >>> b.foo_bar
        "should be 'foo_bar' as attribute."
        >>> b["foo-:-bar"]
        "should be 'foo_bar' as attribute."
        >>> b.foo_bar = "changed!"
        >>> b == {'1': "should be 'int_1' as attribute", 'best pony': 'Littlepip', 'foo_bar': 'changed!', 'foo-:-bar': 'changed!', 'a': {'b': {'c': {'e': 'barz2', 'd': 'foo'}}}}
        True
        >>> b.foo_bar
        'changed!'
        >>> b["foo-:-bar"]
        'changed!'
        >>> b["foo-:-bar"] = "changed again!"
        >>> b.foo_bar
        'changed again!'
        >>> b["foo-:-bar"]
        'changed again!'
        >>> b["foo...bar"] = "heya"
        <BLANKLINE>
        CRITICAL WARNING in DictObject: Mapped key 'foo...bar' to attribute 'foo_bar_1', because attribute 'foo_bar' was already set by key 'foo-:-bar'.
        >>> b == {'foo-:-bar': 'changed again!', 'foo...bar': 'heya', '1': "should be 'int_1' as attribute", 'foo_bar': 'changed!', 'best pony': 'Littlepip', 'a': {'b': {'c': {'e': 'barz2', 'd': 'foo'}}}}
        True
        >>> b.foo_bar
        'changed again!'
        >>> b["foo-:-bar"]
        'changed again!'
        >>> b.hello = 'world'
        >>> b.hello
        'world'
        >>> b['hello'] += "!"
        >>> b.hello
        'world!'


        >>> b = DictObject(ponies='are pretty!')
        >>> 'ponies' in b
        True
        >>> 'foo' in b
        False
        >>> b['foo'] = 42
        >>> 'foo' in b
        True
        >>> b.hello = 'hai'
        >>> 'hello' in b
        True
        >>> b[None] = 123
        >>> None in b
        True
        >>> b[False] = 456
        >>> False in b
        True

        >>> m = DictObject()
        >>> m
        {}

        >>> m.hua = [{"hey":"heeey!"}]
        >>> m.hua[0].hey
        'heeey!'

        Python 2 with unicode:
        >>> from luckydonaldUtils.encoding import to_unicode as u
        >>> h = DictObject(ponies=u('are pretty!'))
        >>> h.ponies == u('are pretty!')
        True
        >>> i = DictObject({u("key"):u("value")})
        >>> i.key == u("value")
        True
        >>> i[u("key")] == u("value")
        True
        >>> i["key"] == u("value")
        True
        >>> i["key"] == i[u("key")] == i.key
        True


    """
    pass

def ______do_pickle_tests______():
    """
    >>> # from DictObject import DictObject
    >>> import pickle; from io import BytesIO;f = BytesIO()
    >>> d = DictObject.objectify({"some key": 123})
    >>> d == {"some key": 123}
    True
    >>> d['some key']
    123
    >>> d.some_key
    123
    >>> pickle.dump(d, f)
    >>> f.seek(0)
    0
    >>> o = pickle.load(f)
    >>> del f
    >>> o.some_key
    123
    >>> o['some key']
    123

    Now a more complex one:

    >>> d = DictObject.objectify({'a dict': {'a boolean': True, 'a list': [1,2,3,True, ["foo", {"lel": "so many levels"}]]}})

    Check the original stuff first, that must work

    >>> d.a_dict.a_boolean
    True
    >>> d['a dict']['a boolean']
    True
    >>> d.a_dict.a_list[0]
    1
    >>> d['a dict']['a list'][0]
    1
    >>> d.a_dict.a_list == [1,2,3,True, ["foo", {"lel": "so many levels"}]]
    True
    >>> d['a dict']['a list'] == [1,2,3,True, ["foo", {"lel": "so many levels"}]]
    True
    >>> d.a_dict.a_list[4][1].lel
    'so many levels'
    >>> d['a dict']['a list'][4][1]['lel']
    'so many levels'

    >>> f = BytesIO()
    >>> pickle.dump(d, f)
    >>> f.seek(0)
    0
    >>> o = pickle.load(f)
    >>> del f

    Hua
    >>> o.a_dict.a_list == [1,2,3,True, ["foo", {"lel": "so many levels"}]]
    True
    >>> o['a dict']['a list'] == [1,2,3,True, ["foo", {"lel": "so many levels"}]]
    True
    >>> o.a_dict.a_list[4][1].lel
    'so many levels'
    >>> o['a dict']['a list'][4][1]['lel']
    'so many levels'

    :return:
    """
    pass

pass
