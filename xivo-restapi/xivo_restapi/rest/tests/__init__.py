from functools import wraps
from mock import Mock
from xivo_restapi.rest.authentication import xivo_realm_digest
from xivo_restapi.rest.negotiate import flask_negotiate

def mock_basic_decorator(func):
    return func


def mock_parameterized_decorator(string):
    def decorated(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorated

xivo_realm_digest.realmDigest = Mock()
xivo_realm_digest.realmDigest.requires_auth.side_effect = mock_basic_decorator
flask_negotiate.consumes = Mock()
flask_negotiate.consumes.side_effect = mock_parameterized_decorator
flask_negotiate.produces = Mock()
flask_negotiate.produces.side_effect = mock_parameterized_decorator
