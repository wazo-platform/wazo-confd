# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import csv
import json
import logging
import pprint
from cStringIO import StringIO

from hamcrest import assert_that, is_in, has_key, has_entry, contains_string, has_item, instance_of, only_contains
import requests
from urls import UrlFragment
from .config import confd_base_url

requests.packages.urllib3.disable_warnings()


logger = logging.getLogger(__name__)


class ConfdClient(object):

    DEFAULT_HEADERS = {'Accept': 'application/json',
                       'Content-Type': 'application/json'}

    @classmethod
    def from_options(cls, host, port, username, password, https=True, headers=None, encoder=None):
        url = confd_base_url(host, port, https)
        logger.info('CONFD URL: %s', url)
        return cls(url, username, password, headers, encoder)

    def __init__(self, base_url, username, password, headers=None, encoder=None):
        self.base_url = base_url
        self.encode = encoder or self._encode_dict
        self.session = requests.Session()
        self.session.verify = False
        self.session.auth = requests.auth.HTTPDigestAuth(username, password)
        self.session.headers.update(headers or self.DEFAULT_HEADERS)

    def request(self, method, url, parameters=None, data=None):
        full_url = self._build_url(url)
        data = self.encode(data)
        self.log_request(method, full_url, parameters, data)

        response = self.session.request(method, full_url, params=parameters, data=data)
        logger.debug('Response - %s %s', response.status_code, response.text)

        return Response(response)

    def log_request(self, method, url, parameters, data):
        if data is not None:
            data = unicode(data, encoding='utf8')
        logger.info(u'%s %s params: %s body: %s', method, url, parameters, data)

    def get(self, url, **parameters):
        return self.request('GET', url, parameters=parameters)

    def post(self, url, body):
        return self.request('POST', url, data=body)

    def put(self, url, body):
        return self.request('PUT', url, data=body)

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

    def __init__(self, client, fragments, body=None):
        super(RestUrlClient, self).__init__(fragments)
        self.client = client
        self.body = body or {}

    def __repr__(self):
        return "<Client '{}'>".format('/'.join(self.fragments))

    def get(self, **params):
        url = str(self)
        params = self._merge_params(params, self.body)
        return self.client.get(url, **params)

    def post(self, body=None, **params):
        url = str(self)
        params = self._merge_params(params, body, self.body)
        return self.client.post(url, params)

    def put(self, body=None, **params):
        url = str(self)
        params = self._merge_params(params, body, self.body)
        return self.client.put(url, params)

    def delete(self):
        url = str(self)
        return self.client.delete(url)

    def _copy(self):
        return self.__class__(self.client, list(self.fragments), dict(self.body))

    def _add_body(self, body):
        self.body.update(body)
        return self

    def _merge_params(self, *maps):
        params = {}
        for mapping in reversed(maps):
            if mapping:
                params.update(mapping)
        return params

    def __call__(self, fragment=None, **body):
        url = self._copy()
        if fragment:
            url._add(fragment)
        if body:
            url._add_body(body)
        return url


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

    @property
    def total(self):
        self.assert_ok()
        assert_that(self.json, has_key('total'))
        return self.json['total']

    def csv(self):
        self.assert_ok()
        lines = []
        content = StringIO(self.response.content)
        reader = csv.DictReader(content)
        for row in reader:
            lines.append({key.decode('utf8'): value.decode('utf8')
                          for key, value in row.iteritems()})
        return lines

    def assert_status(self, *statuses):
        assert_that(statuses, only_contains(instance_of(int)))
        assert_that(self.response.status_code, is_in(statuses), self.response.text)

    def assert_ok(self):
        self.assert_status(*self.STATUS_OK)

    def assert_created(self, *resources, **kwargs):
        self.assert_status(201)
        for resource in resources:
            self.assert_location(kwargs.get('location', resource))
            self.assert_link(resource)

    def assert_location(self, resource):
        headers = {key.lower(): value for key, value in self.response.headers.iteritems()}
        expected = has_entry('location', contains_string(resource))
        assert_that(headers, expected, 'Location header not found')

    def assert_link(self, resource):
        expected = has_entry('links', has_item(has_entry('rel', contains_string(resource))))
        assert_that(self.json, expected, 'Resource link not found')

    def assert_updated(self):
        self.assert_status(204)

    def assert_deleted(self):
        self.assert_status(204)

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
