import json
import logging
import pprint

from hamcrest import assert_that, is_in, has_key
import requests
from urls import UrlFragment

requests.packages.urllib3.disable_warnings()


logger = logging.getLogger(__name__)


class ConfdClient(object):

    DEFAULT_HEADERS = {'Accept': 'application/json',
                       'Content-Type': 'application/json'}

    @classmethod
    def from_options(cls, host, port, username, password, https=True, headers=None):
        scheme = 'https' if https else 'http'
        url = "{}://{}:{}/1.1".format(scheme, host, port)
        logger.info('CONFD URL: %s', url)
        return cls(url, username, password, headers)

    def __init__(self, base_url, username, password, headers=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        self.session.auth = requests.auth.HTTPDigestAuth(username, password)
        self.session.headers.update(headers or self.DEFAULT_HEADERS)

    def request(self, method, url, parameters=None, data=None):
        full_url = self._build_url(url)
        data = self._encode_dict(data)

        logger.info('%s %s params: %s body: %s', method, full_url, parameters, data)
        response = self.session.request(method, full_url, params=parameters, data=data)

        logger.debug('Response - %s %s', response.status_code, response.text)
        return Response(response)

    def get(self, url, **parameters):
        return self.request('GET', url, parameters=parameters)

    def post(self, url, data=None, **kwargs):
        data = data or {}
        data.update(kwargs)
        return self.request('POST', url, data=data)

    def put(self, url, data=None, **kwargs):
        data = data or {}
        data.update(kwargs)
        return self.request('PUT', url, data=data)

    def delete(self, url):
        return self.request('DELETE', url)

    def _encode_dict(self, parameters=None):
        if parameters is not None:
            return json.dumps(parameters)
        return None

    def _build_url(self, url):
        return '/'.join((self.base_url, url.lstrip('/')))

    @property
    def url(self):
        return RestUrlClient(self, [''])


class RestUrlClient(UrlFragment):

    def __init__(self, client, fragments):
        super(RestUrlClient, self).__init__(fragments)
        self.client = client

    def _build(self, fragments):
        return RestUrlClient(self.client, fragments)

    def get(self, **params):
        url = str(self)
        return self.client.get(url, **params)

    def post(self, data=None, **params):
        url = str(self)
        return self.client.post(url, data, **params)

    def put(self, data=None, **params):
        url = str(self)
        return self.client.put(url, data, **params)

    def delete(self):
        url = str(self)
        return self.client.delete(url)


class Response(object):

    STATUS_OK = (200, 201, 204)

    def __init__(self, response):
        self.response = response

    def __repr__(self):
        return '<{} {}\n{}\n>'.format(self.__class__.__name__,
                                      self.response.status_code,
                                      pprint.pformat(self.json))

    @property
    def raw(self):
        return self.response.text

    @property
    def json(self):
        return self.response.json() if self.response.text else None

    @property
    def item(self):
        self.assert_ok()
        return self.json

    @property
    def status(self):
        return self.response.status_code

    @property
    def items(self):
        self.assert_ok()
        assert_that(self.json, has_key('items'))
        return self.json['items']

    def assert_status(self, *statuses):
        assert_that(self.response.status_code, is_in(statuses), self.response.text)

    def assert_ok(self):
        self.assert_status(*self.STATUS_OK)

    def assert_match(self, status, assertion):
        self.assert_status(status)
        if hasattr(assertion, 'assert_match'):
            assertion.assert_match(self.json)
        elif hasattr(assertion, 'search'):
            match = assertion.search(self.raw)
            explanation = "regex {} did not match on {}"
            assert_that(match is not None, explanation.format(assertion.pattern, self.raw))
        else:
            raise AssertionError("Unable to assert on '{}'".format(repr(assertion)))
