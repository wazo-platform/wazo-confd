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
                              RestAPIConfig.XIVO_VOICEMAIL_SERVICE_PATH + "/", "")
        self.instance_voicemail_management.get_all_voicemails.assert_any_call()
        self.assertEquals(result.status, status)
        self.assertEquals(rest_encoder.encode(expected_result), result.data)

    def test_list_error(self):
        status = "500 INTERNAL SERVER ERROR"

        def mock_get_all_users():
            raise Exception()

        self.instance_voicemail_management.get_all_voicemails.side_effect = mock_get_all_users
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_VOICEMAIL_SERVICE_PATH + "/", "")
        self.instance_voicemail_management.get_all_voicemails.assert_any_call()
        self.assertEquals(result.status, status)
        self.instance_voicemail_management.get_all_voicemails.side_effect = None
