class TestServer:
    @staticmethod
    def test_is_running(server):
        func = server.is_running

        assert func(), "Did you forget to run redis ? Or did you get the port wrong ?"

    @staticmethod
    def test_set_value(server):
        func = server.set_value

        prefix = "[__useless_key__]"

        args = [
            ["0", 1234, None, False],
            ["1", 1111, {"hours": 10}, False],
            ["2", {1: "a", 2: "b"}, None, False],
        ]

        for key, value, expire_in, hmap in args:
            key = prefix + key
            func(key, value, expire_in, hmap)

            value_stored = server.get_value(key)

            assert value == value_stored
