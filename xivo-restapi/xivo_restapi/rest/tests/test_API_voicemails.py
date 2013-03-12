# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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

from xivo_dao.alchemy.voicemail import Voicemail
from xivo_restapi.rest import rest_encoder
from xivo_restapi.rest.tests import instance_voicemail_management
from xivo_restapi.restapi_config import RestAPIConfig
from xivo_restapi.services.utils.exceptions import NoSuchElementException
import unittest


class Test(unittest.TestCase):

    def setUp(self):
        self.instance_voicemail_management = instance_voicemail_management
        from xivo_restapi.rest import flask_http_server
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    def test_list_success(self):
        status = "200 OK"
        voicemail1 = Voicemail()
        voicemail1.mailbox = "123"
        voicemail2 = Voicemail()
        voicemail2.mailbox = "456"
        expected_list = [voicemail1, voicemail2]
        expected_result = {"items": expected_list}
        self.instance_voicemail_management.get_all_voicemails.return_value = expected_list
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_VOICEMAIL_SERVICE_PATH + "/")
        self.instance_voicemail_management.get_all_voicemails.assert_any_call()
        self.assertEquals(result.status, status)
        self.assertEquals(rest_encoder.encode(expected_result), result.data)

    def test_list_error(self):
        status = "500 INTERNAL SERVER ERROR"

        def mock_get_all_users():
            raise Exception()

        self.instance_voicemail_management.get_all_voicemails.side_effect = mock_get_all_users
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_VOICEMAIL_SERVICE_PATH + "/")
        self.instance_voicemail_management.get_all_voicemails.assert_any_call()
        self.assertEquals(result.status, status)
        self.instance_voicemail_management.get_all_voicemails.side_effect = None

    def test_edit_success(self):
        status = "200 OK"
        self.instance_voicemail_management.edit_voicemail.return_value = True
        data = {"mailbox": "123",
                "fullname": "test"}
        result = self.app.put(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_VOICEMAIL_SERVICE_PATH + "/1",
                              data=rest_encoder.encode(data))
        self.instance_voicemail_management.edit_voicemail.assert_called_with(1, data)
        self.assertEquals(status, result.status)

    def test_edit_empty_data(self):
        status = "400 BAD REQUEST"
        result = self.app.put(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_VOICEMAIL_SERVICE_PATH + "/1")
        self.assertEquals(status, result.status)

    def test_edit_unexisting_voicemail(self):
        status = "404 NOT FOUND"
        data = {"mailbox": "123",
                "fullname": "test"}

        def mock_edit_voicemail(voicemaiid, data):
            raise NoSuchElementException('')

        self.instance_voicemail_management.edit_voicemail.side_effect = mock_edit_voicemail
        result = self.app.put(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_VOICEMAIL_SERVICE_PATH + "/1",
                              data=rest_encoder.encode(data))
        self.instance_voicemail_management.edit_voicemail.assert_called_with(1, data)
        self.assertEquals(status, result.status)
        self.instance_voicemail_management.edit_voicemail.side_effect = None

    def test_edit_invalid_data(self):
        status = "400 BAD REQUEST"
        data = {"mailbox": "123",
                "fullname": "test",
                "unexisting_field": "value"}
        self.instance_voicemail_management.edit_voicemail.return_value = True
        result = self.app.put(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_VOICEMAIL_SERVICE_PATH + "/1",
                              data=rest_encoder.encode(data))
        self.assertEquals(result.status, status)
        returned_data = rest_encoder.decode(result.data)
        self.assertEquals(returned_data, ["Incorrect parameters sent: unexisting_field"])
