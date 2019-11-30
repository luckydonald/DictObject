from DictObject import DictObject
import json
import os
import logging

__author__ = 'luckydonald'

logger = logging.getLogger(__name__)


class AutosaveDictObject(DictObject):
    """
        Sooo.

            >>> with open("./test.json", "w") as file:
            ... 	json.dump({'foo': 'bar', 'numbers': [1, 2, 3], 'hurr': 'durr', 'boolean': True, 'dev-null': 0}, file)
            >>> a = AutosaveDictObject()
            Traceback (most recent call last):
                ...
                a = AutosaveDict()
            TypeError: __init__() missing 1 required positional argument: 'file'

            >>> a = AutosaveDictObject("./test.json")
            >>> a.foor
            Traceback (most recent call last):
                ...
            AttributeError: foor
            >>> a = AutosaveDictObject("./test.json")
            >>> a == {'foo': 'bar', 'numbers': [1, 2, 3], 'hurr': 'durr', 'boolean': True, 'dev-null': 0}
            True
            >>> a["foo"]
            'bar'
            >>> a.foo
            'bar'
            >>> a.foo = "hey"
            >>> a.foo
            'hey'
            >>> b = AutosaveDictObject("./test.json")
            >>> b.foo
            'hey'
            >>> b["foo"]
            'hey'
            >>> b.enable_autosave(False)
            >>> b["foo"] = "hurr"
            >>> b.foo
            'hurr'
            >>> c = AutosaveDictObject("./test.json")
            >>> c.foo
            'hey'
            >>> b.store_database()
            >>> c.load_database()
            >>> c.foo
            'hurr'
            >>> c.numbers == [1, 2, 3]
            True
            >>> c.foo = "I am from .json!"
            >>> d = AutosaveDictObject("./test.json", {'foo': 'changed', 'default': 'this is not in the .json file.', 'numbers':'different type example', 'test':{'more':'stuff'}})
            >>> d.foo
            'I am from .json!'
            >>> d.default
            'this is not in the .json file.'
            >>> d.numbers == [1, 2, 3]
            True
            >>> d.test
            {'more': 'stuff'}
            >>> d.merge_dict({'foo':'should be overwriten by this.'})
            >>> d.foo
            'should be overwriten by this.'

            Create new file test.
            >>> b = AutosaveDictObject("./test2.json")
            >>> import os
            >>> os.remove("./test2.json")


    """

    def __init__(self, file, *args, autosafe=True, path=None, load_now=True, defaults=None, **kwargs):
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
        try:
            with open(self._database_file, "r") as file:
                json_data = file.read()
        except IOError as e:
            logger.warn("File {file!r} could not be loaded! Error {e}".format(file=self._database_file, e=e))
            raise
        # end def
        data = self._str_to_json(json_data)
        if not merge:
            logging.debug("Not merging.")
            self._attribute_to_key_map.clear()
            self.clear()
            DictObject.__init__(self, data)
        else:
            logging.debug("Merging data.")
            self.merge_dict(data)
