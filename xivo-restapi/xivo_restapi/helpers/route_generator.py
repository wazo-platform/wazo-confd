from xivo_restapi.helpers.common import exception_catcher
from xivo_restapi.authentication.xivo_realm_digest import realmDigest
from xivo_restapi.negotiate.flask_negotiate import produces, consumes


class RouteGenerator(object):

    def __init__(self, blueprint):
        self._blueprint = blueprint

    def __call__(self, route, *args, **kwargs):
        def decorator(func):
            func = exception_catcher(func)
            func = self._blueprint.route(route, *args, **kwargs)(func)
            func = realmDigest.requires_auth(func)
            func = produces('application/json')(func)
            func = consumes('application/json')(func)
        return decorator
