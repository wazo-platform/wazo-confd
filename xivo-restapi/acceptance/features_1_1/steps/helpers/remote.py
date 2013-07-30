import execnet

from acceptance.helpers.config import get_config_value


def remote_exec(func, **kwargs):
    host = get_config_value('xivo', 'hostname')
    username = 'root'

    gw = execnet.makegateway('ssh=%s@%s' % (username, host))

    channel = gw.remote_exec(func, **kwargs)
    channel.waitclose()
