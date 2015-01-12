# -*- coding: UTF-8 -*-

# Copyright (C) 2013 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

import logging
import sys
import unittest

from flask.testing import FlaskClient
from hamcrest import assert_that, equal_to, has_entries, is_in, has_items, has_key, contains

from xivo_confd import config
from xivo_confd.helpers import serializer
from xivo_confd.helpers.common import handle_error
from xivo_confd.rest_api import CoreRestApi


class TestClient(FlaskClient):

    def open(self, *args, **kwargs):
        kwargs.setdefault('environ_base', {})['REMOTE_ADDR'] = '127.0.0.1'
        return super(TestClient, self).open(*args, **kwargs)

    def get(self, *args, **kwargs):
        kwargs.setdefault('headers', {'Accept': 'application/json'})
        return super(TestClient, self).get(*args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        kwargs.setdefault('headers', {'Accept': 'application/json'})
        return super(TestClient, self).put(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs.setdefault('content_type', 'application/json')
        kwargs.setdefault('headers', {'Accept': 'application/json'})
        return super(TestClient, self).post(*args, **kwargs)


class TestResources(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        rest_api = CoreRestApi(config.DEFAULT_CONFIG)
        rest_api.app.config['TESTING'] = True
        rest_api.app.test_client_class = TestClient
        cls.app = rest_api.app.test_client()

        @rest_api.app.errorhandler(Exception)
        def _handle_error(error):
            return handle_error(error)

    def _serialize_encode(self, data):
        return serializer.encode(data).encode('utf8')

    def _serialize_decode(self, data):
        return serializer.decode(data)

    def assert_response(self, response, status_code, expected):
        assert_that(status_code, equal_to(response.status_code))
        assert_that(self._serialize_decode(response.data), equal_to(expected))

    def assert_response_for_list(self, response, expected):
        assert_that(response.status_code, equal_to(200))

        data = self._serialize_decode(response.data)
        assert_that(data, has_key('total'))
        assert_that(data, has_key('items'))

        list_assertion = contains(*(self._build_assertion(i) for i in data['items']))
        assert_that(data['items'], list_assertion)

    def assert_response_for_get(self, response, expected):
        assert_that(response.status_code, equal_to(200))
        assert_that(self._serialize_decode(response.data), self._build_assertion(expected))

    def assert_response_for_create(self, response, expected):
        assert_that(response.status_code, equal_to(201))
        assert_that(self._serialize_decode(response.data), self._build_assertion(expected))

    def assert_response_for_update(self, response):
        assert_that(response.status_code, equal_to(204))
        assert_that(response.data, equal_to(''))

    def assert_response_for_delete(self, response):
        assert_that(response.status_code, equal_to(204))
        assert_that(response.data, equal_to(''))

    def assert_error(self, response, regex=None, statuses=None):
        statuses = statuses or (400, 404)
        assert_that(response.status_code, is_in(statuses))
        if regex:
            assert_that(regex.search(response.data), response.data)

    def _build_assertion(self, item):
        assertion = dict(item)
        if 'links' in assertion:
            assertion['links'] = has_items(*(l for l in assertion['links']))
        return has_entries(assertion)
