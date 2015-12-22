import inspect

from functools import wraps


class IsolatedAction(object):

    actions = {}

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        if inspect.isgeneratorfunction(func):
            @wraps(func)
            def generator_decorated(*args, **kwargs):
                resource = self.__enter__()
                new_args = list(args) + [resource]
                for result in func(*new_args, **kwargs):
                    yield result
                self.__exit__()
            return generator_decorated
        else:
            @wraps(func)
            def decorated(*args, **kwargs):
                resource = self.__enter__()
                new_args = list(args) + [resource]
                result = func(*new_args, **kwargs)
                self.__exit__()
                return result
            return decorated

    def __enter__(self):
        callback = self.actions['generate']
        self.resource = callback(*self.args, **self.kwargs)
        return self.resource

    def __exit__(self, *args):
        callback = self.actions.get('delete')
        if callback:
            callback(self.resource['id'], check=False)
