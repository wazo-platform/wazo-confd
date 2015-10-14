from wrappers import IsolatedAction

from test_api.setup import setup_sysconfd, setup_provd


class sysconfd(IsolatedAction):

    actions = {'generate': setup_sysconfd}


class provd(IsolatedAction):

    actions = {'generate': setup_provd}
