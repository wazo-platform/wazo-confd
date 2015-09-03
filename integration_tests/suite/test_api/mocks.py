from wrappers import IsolatedAction

from test_api.setup import setup_sysconfd


class sysconfd(IsolatedAction):

    actions = {'generate': setup_sysconfd}
