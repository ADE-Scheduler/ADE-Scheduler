from itertools import chain


def return_diagnostic(*args):
    return list(args)


def test_redis():
    from redis import Redis
    r = Redis(host='localhost', port=6379)
    error1 = None
    try:
        r.ping()
    except:
        error1 = 'Could not connect to Redis server.'

    return return_diagnostic(error1)


def test_credentials():
    from backend.credentials import Credentials
    error1 = None
    try:
        Credentials.get_credentials(Credentials.ADE_API_CREDENTIALS)
    except KeyError:
        error1 = 'Credentials for ADE API not found.'

    error2 = None
    try:
        Credentials.get_credentials(Credentials.GMAIL_CREDENTIALS)
    except KeyError:
        error2 = 'Credentials for GMAIL not found.'

    return Diagnostician.return_diagnostic(error1, error2)


def ready_to_initialize():
    tests = [
        test_redis,
        test_credentials
    ]

    diagnostics = list(
        chain.from_iterable(
            test() for test in tests
        )
    )

    errors = list(filter(None, diagnostics))

    if not errors:
        return True, None
    else:
        return False, errors
