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
        self.requests = []

    def exec_request_handlers(self, args):
        if self.dao.is_live_reload_enabled():
            url = "{}/exec_request_handlers".format(self.base_url)
            body = json.dumps(args)
            self.add_request('POST', url, data=body)

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
        for action, url, params, data in self.requests:
            response = session.request(action, url, params=params, data=data)
            self.check_for_errors(response)

    def rollback(self):
        self.requests = []
