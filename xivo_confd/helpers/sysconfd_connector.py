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

import requests
import json

from xivo_dao.resources.configuration import dao as configuration_dao

SYSCONFD_SERVER = "localhost"
SYSCONFD_PORT = "8668"


class SysconfdError(Exception):
    def __init__(self, code, value):
        self.code = code
        self.value = value

    def __str__(self):
        return "sysconfd error: status {} - {}".format(self.code, self.value)


class SysconfdClient(object):

    @classmethod
    def with_host_port(cls, host, port):
        url = "http://{}:{}".format(host, port)
        return cls(url, configuration_dao)

    def __init__(self, base_url, dao):
        self.base_url = base_url
        self.dao = dao

    def exec_request_handlers(self, args):
        if self.dao.is_live_reload_enabled():
            url = "{}/exec_request_handlers".format(self.base_url)
            body = json.dumps(args)
            response = self._session().post(url, data=body)
            self.check_for_errors(response)

    def move_voicemail(self, old_number, old_context, number, context):
        params = {'old_mailbox': old_number,
                  'old_context': old_context,
                  'new_mailbox': number,
                  'new_context': context}
        url = "{}/move_voicemail".format(self.base_url)
        response = self._session().get(url, params=params)
        self.check_for_errors(response)

    def delete_voicemail(self, number, context):
        params = {'mailbox': number,
                  'context': context}
        url = "{}/delete_voicemail".format(self.base_url)
        response = self._session().get(url, params=params)
        self.check_for_errors(response)

    def _session(self):
        session = requests.Session()
        session.trust_env = False
        return session

    def check_for_errors(self, response):
        if response.status_code != 200:
            raise SysconfdError(response.status_code,
                                response.text)


def setup_sysconfd(host, port):
    global SYSCONFD_SERVER
    global SYSCONFD_PORT
    SYSCONFD_SERVER = host
    SYSCONFD_PORT = port


def new_client():
    return SysconfdClient.with_host_port(SYSCONFD_SERVER, SYSCONFD_PORT)


def exec_request_handlers(args):
    new_client().exec_request_handlers(args)
