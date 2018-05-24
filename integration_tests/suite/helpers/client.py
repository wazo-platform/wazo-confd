# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

import csv
import json
import logging
import pprint
import requests
import sys

from io import BytesIO
from hamcrest import (
    assert_that,
    contains_string,
    ends_with,
    has_entry,
    has_item,
    has_key,
    instance_of,
    is_in,
    only_contains,
)

from .urls import UrlFragment


requests.packages.urllib3.disable_warnings()


logger = logging.getLogger(__name__)


class ConfdClient(object):

    DEFAULT_HEADERS = {'Accept': 'application/json',
                       'X-Auth-Token': 'valid-token-multitenant',  # hardcoded in xivo-auth-mock
                       'Content-Type': 'application/json'}

    @classmethod
    def from_options(cls, host, port, username=None, password=None, https=True, headers=None, encoder=None):
        url = '{}://{}:{}/1.1'.format('https' if https else 'http', host, port)
        logger.info('CONFD URL: %s', url)
        return cls(url, username, password, headers, encoder)

    def __init__(self, base_url, username, password, headers=None, encoder=None):
        self.base_url = base_url
        self.encode = encoder or self._encode_dict
        self.session = requests.Session()
        self.session.verify = False
        self.session.auth = requests.auth.HTTPDigestAuth(username, password)
        self.session.headers.update(headers or self.DEFAULT_HEADERS)

    def request(self, method, url, parameters=None, data=None, headers=None):
        full_url = self._build_url(url)
        data = self.encode(data)
        self.log_request(method, full_url, parameters, data)

        response = self.session.request(method, full_url, params=parameters, data=data, headers=headers)
        logger.debug('Response - %s %s', response.status_code, response.text)

        return Response(response)

    def log_request(self, method, url, parameters, data):
        if sys.version_info[0] == 2:
            data = unicode(data, encoding='utf8') if data is not None else data
        logger.info('%s %s params: %s body: %s', method, url, parameters, data)

    def head(self, url, **parameters):
        return self.request('HEAD', url, parameters=parameters)

    def get(self, url, **parameters):
        return self.request('GET', url, parameters=parameters)

    def post(self, url, body, headers=None):
        kwargs = {'data': body}
        if headers:
            kwargs['headers'] = headers
        return self.request('POST', url, **kwargs)

    def put(self, url, body, parameters=None):
        return self.request('PUT', url, data=body, parameters=parameters)

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

    def head(self, **params):
        url = str(self)
        params = self._merge_params(params, self.body)
        return self.client.head(url, **params)

    def get(self, **params):
        url = str(self)
        params = self._merge_params(params, self.body)
        return self.client.get(url, **params)

    def post(self, body=None, wazo_tenant=None, **params):
        url = str(self)
        params = self._merge_params(params, body, self.body)
        headers = {'Wazo-Tenant': wazo_tenant} if wazo_tenant else None
        return self.client.post(url, params, headers=headers)

    def put(self, body=None, query_string=None, **params):
        url = str(self)
        params = self._merge_params(params, body, self.body)
        return self.client.put(url, params, query_string)

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
        content = BytesIO(self.response.content)
        reader = csv.DictReader(content)
        for row in reader:
            lines.append({key.decode('utf8'): value.decode('utf8')
                          for key, value in row.items()})
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
        headers = {key.lower(): value for key, value in self.response.headers.items()}
        expected = has_entry('location', contains_string(resource))
        assert_that(headers, expected, 'Location header not found')

    def assert_content_disposition(self, filename):
        headers = {key.lower(): value for key, value in self.response.headers.items()}
        expected = has_entry('content-disposition', ends_with('filename={}'.format(filename)))
        assert_that(headers, expected, 'Content-Disposition header not found')

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
