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

import unittest
from mock import Mock, patch
from xivo.agi import AGI
from gevent.httplib import HTTPConnection, HTTPResponse
import random
from gevent import http
from xivo_recording.recording_config import RecordingConfig

mock_agi = Mock(AGI)
mock_http_connection = Mock(HTTPConnection)


class TestXivoRecordingAgi(unittest.TestCase):

    def setUp(self):
        self.xivo_queue_name = 'xivo_name'
        self.base_filename = 'base_filename' + str(random.randint(100, 999))
        self.rest_response = '[{"base_filename": "' + self.base_filename + '", "queue_id": "1", "activated": "True", "campaign_name": "test"}]'

        self.patcher_agi = patch("xivo.agi.AGI")
        mock_patch_agi = self.patcher_agi.start()
        self.instance_agi = mock_agi
        mock_patch_agi.return_value = self.instance_agi

        self.patcher_http_connection = patch("gevent.httplib.HTTPConnection")
        mock_patch_http_connection = self.patcher_http_connection.start()
        self.instance_http_connection = mock_http_connection
        mock_patch_http_connection.return_value = self.instance_http_connection

    def tearDown(self):
        self.patcher_agi.stop()
        self.patcher_http_connection.stop()

    def test_xivo_recording_agi_get_variables(self):
        self.instance_agi.get_variable.return_value = self.xivo_queue_name
        from bin import xivo_recording_agi
        xivo_recording_agi.get_variables()
        self.instance_agi.get_variable.assert_called_with("XIVO_QUEUENAME")

    def test_xivo_recording_agi_get_campaigns(self):
        response = Mock()
        response.read.return_value = self.rest_response
        response.status = "200"

        self.instance_http_connection.getresponse.return_value = response

        self.instance_agi.set_variable.return_value = 0
        from bin import xivo_recording_agi
        xivo_recording_agi.get_campaigns(self.xivo_queue_name)

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + \
                        '/?activated=true&queue_name=' + self.xivo_queue_name
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        self.instance_http_connection.request.assert_called_with("GET", requestURI, None, headers)

    def test_xivo_recording_agi_extract_base_filename(self):
        from bin import xivo_recording_agi
        extracted_base_filename = xivo_recording_agi.extract_base_filename(self.rest_response)
        self.assertTrue(extracted_base_filename == self.base_filename)


