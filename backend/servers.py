from redis import Redis
from redis.exceptions import ConnectionError
from datetime import timedelta
from typing import Optional, Dict, Any, Tuple, List
from pickle import dumps, loads


class Server(Redis):
    """
    Subclass of Redis object, aiming to simplify the use of the server to few basic commands.

    :param args: arguments passed to parent constructor
    :type arg: Any
    :param kwargs: keyword arguments passed to parent constructor
    :type kwarg: Any

    :Example:

    >>> s = Server(host='localhost', port=6379)
    """
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

    def is_running(self) -> bool:
        """
        Checks whether the server is running.

        :return: True if the server is running
        :rtype: bool
        """
        try:
            self.ping()
            return True
        except ConnectionError:
            return False

    def run(self):
        """
        Runs the server.
        Since redis is an externally run server, it cannot be started from the
        python code properly.
        """
        raise NotImplementedError

    def shutdown(self):
        """
        Shuts the server down.
        """
        super().shutdown(save=True)

    def set_value(self, key: str, value: Any, expire_in: Optional[Dict[str, int]] = None, hmap: bool = False):
        """
        Store a pair key / value in the server, with an optional expiration time.

        :param key: the key
        :type key: str
        :param value: any object that can be dumped (see pickle.dumps)
        :type value: Any
        :param expire_in: dictionary of keyword arguments passed used to create a datetime.timedelta object
        :type expire_in: Optional[Dict[str, int]]
        :param hmap: True if the value passed is a hash-map
        :type hmap: bool

        :Example:

        >>> s.set_value('apple', {'weight': 400, 'unit': 'g'}, expire_in={'hours': 10})
        """
        if hmap:
            self.hmset(key, value)

            if expire_in:
                self.expire(key, timedelta(**expire_in))

        else:
            dumped_value = dumps(value)
            if expire_in:
                self.setex(key, timedelta(**expire_in), dumped_value)
            else:
                self.set(key, dumped_value)

    def contains(self, *keys: str) -> int:
        """
        Returns the number of keys that exist.

        :param keys: key(s) to be checked
        :type keys: str
        :return: the number of keys that exist
        :rtype: int
        """
        return self.exists(*keys)

    def get_value(self, key: str, hmap: Optional[str] = None) -> Any:
        """
        Returns the value with corresponding key stored in the server.

        :param key: the key
        :type key: str
        :param hmap: if present, will look for value stored in hash-map with this name
        :type hmap: str
        :return: the object stored in the server, None if not object matching the key
        :rtype: Any

        :Example:

        >>> s.get_value('apple')
        {'weight': 400, 'unit': 'g'}
        """
        if hmap:
            return self.hmget(hmap, key)
        else:
            value = self.get(key)

            if value:
                return loads(value)
            else:
                return None

    def get_multiple_values(self, *keys, prefix: Optional[str] = '', **kwargs) -> Tuple[List[Any], List[str]]:
        """
        Returns all the values corresponding the given keys. If key does not match any value, the key is returned
        explicitly tell that it is missing. An optional prefix can be added to every key.

        :param keys: the keys
        :type keys: str
        :param prefix: the prefix to be added to each key
        :type prefix: Optional[str]
        :return: a tuple containing all values found and all keys which did not match
        :rtype: Tuple[List[Any], List[str]]
        """
        values = []
        keys_not_found = []

        for key in keys:
            value = self.get_value(prefix + key, **kwargs)
            if value:
                values.append(value)
            else:
                keys_not_found.append(key)

        return values, keys_not_found


if __name__ == '__main__':
    s = Server(host='localhost', port=6379)

    print(s.is_running())

    x = {1: 4, "a": [1, 2, 3]}

    print(dumps(x))

    s.set_value('a', dumps(x))

    yb = s.get_value('a')

    print(yb)

    print(loads(yb))
