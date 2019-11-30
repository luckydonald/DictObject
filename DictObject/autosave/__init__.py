try:
    from .. import DictObject
except (ImportError, ValueError):
    from DictObject import DictObject, DictObjectList
    from luckydonaldUtils.encoding import to_native as n
# end try
import os
import json
import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)


class AutosaveDictObject(DictObject):
    """
        Sooo.

            >>> with open("./test.json", "w") as file:
            ... 	json.dump({'foo': 'bar', 'numbers': [1, 2, 3], 'hurr': 'durr', 'boolean': True, 'dev-null': 0}, file)
            >>> try:
            ...     a = AutosaveDictObject()
            ...     raise AssertionError('should throw a TypeError...')
            ... except TypeError:
            ...     pass

            >>> a = AutosaveDictObject("./test.json")
            >>> a.foor
            Traceback (most recent call last):
                ...
            AttributeError: foor
            >>> a = AutosaveDictObject("./test.json")
            >>> a == {'foo': 'bar', 'numbers': [1, 2, 3], 'hurr': 'durr', 'boolean': True, 'dev-null': 0}
            True
            >>> n(a["foo"])
            'bar'
            >>> n(a.foo)
            'bar'
            >>> a.foo = "hey"
            >>> a.foo
            'hey'
            >>> b = AutosaveDictObject("./test.json")
            >>> n(b.foo)
            'hey'
            >>> n(b["foo"])
            'hey'
            >>> b.enable_autosave(False)
            >>> b["foo"] = "hurr"
            >>> b.foo
            'hurr'
            >>> c = AutosaveDictObject("./test.json")
            >>> n(c.foo)
            'hey'
            >>> b.store_database()
            >>> c.load_database()
            >>> n(c.foo)
            'hurr'
            >>> c.numbers == [1, 2, 3]
            True
            >>> c.foo = "I am from .json!"
            >>> d = AutosaveDictObject("./test.json", defaults={'foo': 'changed', 'default': 'this is not in the .json file.', 'numbers':'different type example', 'test':{'more':'stuff'}})
            >>> n(d.foo)
            'I am from .json!'
            >>> d.default
            'this is not in the .json file.'
            >>> d.numbers == [1, 2, 3]
            True
            >>> d.test
            {'more': 'stuff'}
            >>> _ = d.merge_dict({'foo':'should be overwriten by this.'})
            >>> d.foo
            'should be overwriten by this.'

            Create new file test.
            >>> b = AutosaveDictObject("./test2.json", load_now=False)
            >>> b
            {}
            >>> import os
            >>> os.path.exists("./test2.json")   # not yet created
            False
            >>> b.test = 'something to trigger writing to disk'
            >>> os.path.exists("./test2.json")   # not yet created
            True
            >>> os.remove("./test2.json")


    """
    def __init__(self, file, autosafe=True, path=None, load_now=True, defaults=None, *args, **kwargs):
        """
        Initializes the object.

        :param file:  Filename to use.
        :param autosafe: If it should automatically write to disk after values being changed. Default: True
        :param path: The path of the folder where the file is in. Default: None
        :param load_now: If it should load the data from said fail upon creation. Default: True
        :param defaults: Some default dictionary values it should be initialized with. Note that overwrites **kwargs, but not the stuff loaded from file. Default: None
        """
        self.__init_constructor__(autosafe, defaults, file, load_now, path, args, kwargs)
    # end def
    # end if

    def __init_constructor__(self, autosafe, defaults, file, load_now, path, args, kwargs):
        if path:
            file = os.path.join(path, file)
        super(AutosaveDictObject, self).__init__(*args, **kwargs)
        if defaults:
            if isinstance(defaults, dict):
                self.merge_dict(defaults)
            else:
                raise TypeError("Given default is not a dict subclass.")
        self._database_file = file
        self._autosafe = autosafe
        if load_now:
            try:
                self.load_database(merge=True)
            except IOError as e:
                import errno
                if e.errno == errno.ENOENT:
                    logger.warn("File {file!r} could not be found! Not loading any data! Error {e}".format(file=self._database_file, e=e))
                    return
                # end if
            except (ValueError, TypeError, Exception):
                raise

    def after_set(self, key, value_to_set):
        if self._autosafe:
            self.store_database()
            # super(AutosaveDictObject, self).after_set()
        # end if
    # end def

    @staticmethod
    def _parse_object(instance):
        if hasattr(instance, "as_dict"):
            return instance.as_dict()
        else:
            return instance
        # end if
    # end def

    def _json_to_str(self):
        # self still is a dict.
        return json.dumps(self, sort_keys=True, indent=4, separators=(',', ': '),
                                 default=self._parse_object)
    # end def

    def _str_to_json(self, json_data):
        return json.loads(json_data)
    # end def

    def store_database(self):
        logger.debug("Saving AutosaveDictObject to {path}.".format(path=self._database_file))
        json_string = self._json_to_str()
        if not os.path.exists(os.path.dirname(self._database_file)):
            os.makedirs(os.path.dirname(self._database_file))
        with open(self._database_file, "w") as file:  # TODO: create folder.
            file.write(json_string)
            file.flush()
        logger.debug("Saved AutosaveDictObject to {path}".format(path=self._database_file))

    def enable_autosave(self, boolean=True):
        self._autosafe = boolean

    def load_database(self, merge=False):
        logger.debug("Loading database from {file}.".format(file=self._database_file))
        with open(self._database_file, "r") as file:
            json_data = file.read()
        # end with
        data = self._str_to_json(json_data)
        if not merge:
            logging.debug("Not merging.")
            self._attribute_to_key_map.clear()
            self.clear()
            DictObject.__init__(self, data)
        else:
            logging.debug("Merging data.")
            self.merge_dict(data)
