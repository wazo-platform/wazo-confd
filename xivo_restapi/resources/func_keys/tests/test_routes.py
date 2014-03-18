# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from xivo_restapi.helpers.tests.test_resources import TestResources

from flask import Response
from mock import patch
from hamcrest import assert_that, equal_to

BASE_URL = "/1.1/func_keys"


class TestFuncKeyActions(TestResources):

    def assert_response(self, response, status_code, result):
        assert_that(status_code, equal_to(response.status_code))
        assert_that(self._serialize_decode(response.data), equal_to(result))

    @patch('xivo_restapi.resources.func_keys.actions.list')
    def test_list_func_keys(self, list_action):
        expected_status = 200
        expected_item = {'id': 1,
                         'type': 'speeddial',
                         'destination': 'user',
                         'destination_id': 2,
                         'links': [{
                             'href': 'http://localhost/1.1/func_keys/1',
                             'rel': 'func_keys'
                         }]}
        expected_response = {'total': 1,
                             'items': [expected_item]}

        list_action.return_value = Response(self._serialize_encode(expected_response))

        response = self.app.get(BASE_URL)

        list_action.assert_called_once_with()
        self.assert_response(response, expected_status, expected_response)

    @patch('xivo_restapi.resources.func_keys.actions.get')
    def test_get_func_key(self, get_action):
        func_key_id = 1
        expected_status = 200
        expected_response = {'id': func_key_id,
                             'type': 'speeddial',
                             'destination': 'user',
                             'destination_id': 2,
                             'links': [{
                                 'href': 'http://localhost/1.1/func_keys/%s' % func_key_id,
                                 'rel': 'func_keys'
                             }]}

        get_action.return_value = Response(self._serialize_encode(expected_response))

        response = self.app.get("%s/%s" % (BASE_URL, func_key_id))

        get_action.assert_called_once_with(func_key_id)
        self.assert_response(response, expected_status, expected_response)
