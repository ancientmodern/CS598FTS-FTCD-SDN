from pysyncobj import SyncObjConsumer, replicated


class ReplDict(SyncObjConsumer):
    def __init__(self):
        """
        Distributed dict - it has an interface similar to a regular dict.
        """
        super(ReplDict, self).__init__()
        self.__data = {}

    @replicated
    def reset(self, newData):
        """Replace dict with a new one"""
        assert isinstance(newData, dict)
        self.__data = newData

    @replicated
    def __setitem__(self, key, value):
        """Set value for specified key"""
        self.__data[key] = value

    @replicated
    def set(self, key, value):
        """Set value for specified key"""
        self.__data[key] = value

    @replicated
    def setdefault(self, key, default):
        """Return value for specified key, set default value if key not exist"""
        return self.__data.setdefault(key, default)

    @replicated
    def update(self, other):
        """Adds all values from the other dict"""
        self.__data.update(other)

    @replicated
    def pop(self, key, default=None):
        """Remove and return value for given key, return default if key not exist"""
        return self.__data.pop(key, default)

    @replicated
    def clear(self):
        """Remove all items from dict"""
        self.__data.clear()

    def __getitem__(self, key):
        """Return value for given key"""
        return self.__data[key]

    def get(self, key, default=None):
        """Return value for given key, return default if key not exist"""
        return self.__data.get(key, default)

    def __len__(self):
        """Return size of dict"""
        return len(self.__data)

    def __contains__(self, key):
        """True if key exists"""
        return key in self.__data

    def keys(self):
        """Return all keys"""
        return self.__data.keys()

    def values(self):
        """Return all values"""
        return self.__data.values()

    def items(self):
        """Return all items"""
        return self.__data.items()

    def rawData(self):
        """Return internal dict - use it carefully"""
        return self.__data

    @replicated
    def set_nested_item(self, outer_key, inner_key, value):
        """Set value for specified inner_key in the nested dictionary"""
        if outer_key not in self.__data:
            self.__data[outer_key] = {}
        self.__data[outer_key][inner_key] = value

    def get_nested_item(self, outer_key, inner_key, default=None):
        """Return value for specified inner_key in the nested dictionary, return default if key not exist"""
        if outer_key in self.__data:
            return self.__data[outer_key].get(inner_key, default)
        return default

    def print_all(self):
        print(self.__data)
