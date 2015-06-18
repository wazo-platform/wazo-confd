# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from httplib import HTTPConnection
import json
from xivo_dao.resources.configuration import dao as configuration_dao

SYSCONFD_SERVER = "localhost"
SYSCONFD_PORT = "8668"


def setup_sysconfd(host, port):
    global SYSCONFD_SERVER
    global SYSCONFD_PORT
    SYSCONFD_SERVER = host
    SYSCONFD_PORT = port


class SysconfdError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "sysconfd error: %s" % self.value


def sysconfd_conn_request(method, action, args):
    conn = HTTPConnection("%s:%s" % (SYSCONFD_SERVER, SYSCONFD_PORT))
    args = json.dumps(args)
    conn.request(method, action, args)
    res = conn.getresponse()
    if res.status != 200:
        raise SysconfdError('return status %s' % res.status)
    conn.close()


def exec_request_handlers(args):
    if configuration_dao.is_live_reload_enabled():
        sysconfd_conn_request('POST', '/exec_request_handlers', args)


def delete_voicemail_storage(context, number):
    sysconfd_conn_request('GET', '/delete_voicemail?context=%s&name=%s' % (context, number), '')
