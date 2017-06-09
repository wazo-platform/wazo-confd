# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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


class SysconfdError(Exception):
    def __init__(self, code, value):
        self.code = code
        self.value = value

    def __str__(self):
        return "sysconfd error: status {} - {}".format(self.code, self.value)


class SysconfdPublisher(object):

    @classmethod
    def from_config(cls, config):
        url = "http://{}:{}".format(config['sysconfd']['host'],
                                    config['sysconfd']['port'])
        return cls(url, configuration_dao)

    def __init__(self, base_url, dao):
        self.base_url = base_url
        self.dao = dao
        self._reset()

    def exec_request_handlers(self, args):
        if self.dao.is_live_reload_enabled():
            self.add_handlers(args)

    def add_handlers(self, args):
        for service, new_commands in args.iteritems():
            commands = self.handlers.setdefault(service, set())
            commands.update(set(new_commands))

    def move_voicemail(self, old_number, old_context, number, context):
        params = {'old_mailbox': old_number,
                  'old_context': old_context,
                  'new_mailbox': number,
                  'new_context': context}
        url = "{}/move_voicemail".format(self.base_url)
        self.add_request('GET', url, params=params)

    def delete_voicemail(self, number, context):
        params = {'mailbox': number,
                  'context': context}
        url = "{}/delete_voicemail".format(self.base_url)
        self.add_request('GET', url, params=params)

    def commonconf_apply(self):
        url = "{}/commonconf_apply".format(self.base_url)
        self.add_request('GET', url)

    def commonconf_generate(self):
        url = "{}/commonconf_generate".format(self.base_url)
        self.add_request('POST', url, data=json.dumps({}))

    def set_hosts(self, hostname, domain):
        data = {'hostname': hostname,
                'domain': domain}
        url = "{}/hosts".format(self.base_url)
        self.add_request('POST', url, data=json.dumps(data))

    def set_resolvconf(self, nameserver, domain):
        data = {'nameservers': nameserver,
                'search': [domain]}
        url = "{}/resolv_conf".format(self.base_url)
        self.add_request('POST', url, data=json.dumps(data))
        self.flush()

    def xivo_service_start(self):
        data = {'wazo-service': 'start'}
        url = "{}/xivoctl".format(self.base_url)
        self.add_request('POST', url, data=json.dumps(data))

    def xivo_service_enable(self):
        data = {'wazo-service': 'enable'}
        url = "{}/xivoctl".format(self.base_url)
        self.add_request('POST', url, data=json.dumps(data))

    def _session(self):
        session = requests.Session()
        session.trust_env = False
        return session

    def check_for_errors(self, response):
        if response.status_code != 200:
            raise SysconfdError(response.status_code,
                                response.text)

    def add_request(self, action, url, data=None, params=None):
        self.requests.append((action, url, params or {}, data))

    def flush(self):
        session = self._session()
        self.flush_handlers(session)
        self.flush_requests(session)
        self._reset()

    def flush_handlers(self, session):
        if len(self.handlers) > 0:
            url = "{}/exec_request_handlers".format(self.base_url)
            body = {key: tuple(commands)
                    for key, commands in self.handlers.iteritems()}
            response = session.request('POST', url, data=json.dumps(body))
            self.check_for_errors(response)

    def flush_requests(self, session):
        for action, url, params, data in self.requests:
            response = session.request(action, url, params=params, data=data)
            self.check_for_errors(response)

    def rollback(self):
        self._reset()

    def _reset(self):
        self.requests = []
        self.handlers = {}
