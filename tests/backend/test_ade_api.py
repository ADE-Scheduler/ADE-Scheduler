from time import time
import backend.ade_api as ade
from strong.core.decorators import assert_correct_typing


class TestDummyClientImplementation:
    @staticmethod
    def test_is_expired(ade_client):

        func = assert_correct_typing(ade_client.is_expired)
        got = func()
        expected = ade_client.expiration < time()

        assert got == expected

    @staticmethod
    def test_expire_in(ade_client):

        func = assert_correct_typing(ade_client.expire_in)
        t1 = time()
        got = func()
        expected = max(ade_client.expiration - time(), 0)
        t2 = time()
        dt = t2 - t1

        assert abs(got - expected) < dt

    @staticmethod
    def renew_token(ade_client):

        func = assert_correct_typing(ade_client.renew_token)
        got, _ = func()

        assert got is not None

    @staticmethod
    def test_request(ade_client):

        # TODO: expand requests and token tests to test more cases

        func = assert_correct_typing(ade_client.request)
        got = func()

        assert got is not None


def test_get_token(ade_client):

    func = assert_correct_typing(ade.get_token)

    got, _ = func(ade_client.credentials)

    assert got is not None
