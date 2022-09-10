from datetime import timedelta
from pickle import dumps, loads
from typing import Any, Dict, List, Mapping, Optional, Tuple

from redis import Redis
from redis.exceptions import ConnectionError

VALID_TTL_KEYS = [
    "days",
    "seconds",
    "seconds",
    "microseconds",
    "milliseconds",
    "minutes",
    "hours",
    "weeks",
]

REQUIRED_CONFIG_KEYS = [
    "classrooms",
    "course_resources",
    "courses",
    "courses_notify",
    "courses_renotify",
    "events_in_classroom",
    "project_ids",
    "resource_ids",
    "resources",
    "user_session",
]


def parse_redis_ttl_config(conf: Mapping[str, str]) -> Dict[str, Dict[str, int]]:
    """
    Parses a config mapping (from a config file for example) into a usable TTL config.
    Each key, value pair holds the name of the resource stored in the server and the
    parameters to setup the default expiry duration.

    :param conf: the config mapping
    :type conf: Mapping[str, str]
    :return: the TTL config mapping
    :rtype: Dict[str, Dict[str, int]]
    """

    def _parse_ttl(ttl_str):
        key_val = (
            key_val_str.split("=", maxsplit=1) for key_val_str in ttl_str.split(",")
        )
        _ret = {key.strip(): int(val.strip()) for key, val in key_val}

        for key in _ret:
            if key not in VALID_TTL_KEYS:
                raise AttributeError(
                    f"Keyword argument `{key}` is not supported by "
                    f"`timedelta` function, make sure it is in this "
                    f"list {VALID_TTL_KEYS} (case sensitive)"
                )
        return _ret

    ret = {key: _parse_ttl(ttl_str) for key, ttl_str in conf.items()}

    for key in REQUIRED_CONFIG_KEYS:
        if key not in ret:
            raise ValueError(f"The ttl configuration is missing the `{key}` key")

    return ret


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

    def set_value(
        self,
        key: str,
        value: Any,
        expire_in: Optional[Dict[str, int]] = None,
        notify_expire_in: Optional[Dict[str, int]] = None,
        hmap: bool = False,
    ):
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
            self.hset(key, mapping=value)

            if expire_in:
                self.expire(key, timedelta(**expire_in))

        else:
            dumped_value = dumps(value)
            if expire_in:
                self.setex(key, timedelta(**expire_in), dumped_value)
            else:
                self.set(key, dumped_value)

        if notify_expire_in:
            key = f"{key}_is_alive"
            self.setex(key, timedelta(**notify_expire_in), "")

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

    def get_multiple_values(
        self, *keys: str, prefix: str = "", **kwargs
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Returns all the values corresponding the given keys. If key does not match any value, the key is returned
        explicitly tell that it is missing. An optional prefix can be added to every key.

        :param keys: the keys
        :type keys: str
        :param prefix: the prefix to be added to each key
        :type prefix: str
        :return: a tuple containing all values found and all keys which did not match
        :rtype: Tuple[Dict[str, Any], List[str]]
        """
        values = dict()
        keys_not_found = []

        for key in keys:
            value = self.get_value(prefix + key, **kwargs)
            if value:
                # For course combo, a list of courses will be returned
                values[key] = value
            else:
                keys_not_found.append(key)

        return values, keys_not_found

    def get_multiple_values_expired(
        self, *keys: str, prefix: str = ""
    ) -> Tuple[Dict[str, Optional[bool]]]:
        """
        Returns, for each key, wether a expire notification was issued or not, and None is returned if the case the key does not exist.
        An optional prefix can be added to every key.

        :param keys: the keys
        :type keys: str
        :param prefix: the prefix to be added to each key
        :type prefix: str
        :return: a tuple containing all values found and all keys which did not match
        :rtype: Tuple[Dict[str, Optional[bool]]]
        """
        values = dict()

        for key in keys:
            if self.contains(f"{prefix}{key}"):
                value = not self.contains(f"{prefix}{key}_is_alive")
            else:
                value = None
            values[key] = value

        return values
