from functools import wraps


class IsolatedAction(object):

    actions = {}

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwargs):
            user = self.__enter__()
            new_args = list(args) + [user]
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
