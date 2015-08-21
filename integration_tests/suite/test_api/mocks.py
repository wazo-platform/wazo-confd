from wrappers import IsolatedAction

from test_api.sysconfd import new_client


def new_sysconfd():
    client = new_client()
    client.clear()
    return client


class sysconfd(IsolatedAction):

    actions = {'generate': new_sysconfd}
