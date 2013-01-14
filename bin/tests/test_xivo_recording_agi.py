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
from mock import Mock, patch, call
from xivo.agi import AGI
from gevent.httplib import HTTPConnection, HTTPResponse
import random
from gevent import http
from xivo_recording.recording_config import RecordingConfig
from xivo_recording.rest import rest_encoder

mock_agi = Mock(AGI)
mock_http_connection = Mock(HTTPConnection)


class TestXivoRecordingAgi(unittest.TestCase):

    def setUp(self):
        self.xivo_queue_name = 'xivo_name'
        self.xivo_queue_id = random.randint(0, 10)
        self.xivo_campaign_id = random.randint(0, 10)
        self.xivo_srcnum = '2345'
        self.xivo_destnum = '1001'
        self.base_filename = 'filename'
        self.base_filename = 'base_filename' + str(random.randint(100, 999))
        self.rest_response = '[{"base_filename": "' + self.base_filename + '", "queue_name": "queue_1", "activated": "True", "campaign_name": "test"}]'

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

    def test_xivo_recording_agi_get_general_variables(self):
        self.instance_agi.get_variable.return_value = self.xivo_queue_name
        from bin import xivo_recording_agi
        xivo_recording_agi.get_general_variables()
        self.instance_agi.get_variable.assert_called_with("XIVO_DESTNUM")

    def test_xivo_recording_agi_get_detailed_variables(self):
        self.instance_agi.get_variable.return_value = self.xivo_queue_name
        from bin import xivo_recording_agi
        xivo_recording_agi.get_detailed_variables()
        self.instance_agi.get_variable.assert_called_with("QR_QUEUENAME")

    def test_xivo_recording_agi_get_campaigns(self):
        response = Mock()
        response.read.return_value = self.rest_response
        response.status = 200

        self.instance_http_connection.getresponse.return_value = response

        self.instance_agi.set_variable.return_value = 0
        from bin import xivo_recording_agi
        xivo_recording_agi.get_campaigns(self.xivo_queue_id)

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH + \
                        '/?activated=true&queue_id=' + str(self.xivo_queue_id) + \
                        '&running=true'
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        self.instance_http_connection.request.assert_called_with("GET", requestURI, None, headers)

    def mock_get_general_variables(self):
        xivo_vars = {}
        xivo_vars['queue_name'] = self.xivo_queue_name
        xivo_vars['xivo_srcnum'] = self.xivo_srcnum
        xivo_vars['xivo_destnum'] = self.xivo_destnum
        return xivo_vars

    def mock_get_queue_id(self, name):
        if(name == self.xivo_queue_name):
            return self.xivo_queue_id
        else:
            raise Exception

    def mock_get_campaigns(self, queue_id):
        if(queue_id == self.xivo_queue_id):
            return rest_encoder.encode({'data':[{'id': self.xivo_campaign_id, 'activated': "True", 'base_filename': self.base_filename}]})
        else:
            raise Exception

    def test_xivo_recording_determinate_record(self):

        from bin import xivo_recording_agi
        xivo_recording_agi.get_queue_id = self.mock_get_queue_id
        xivo_recording_agi.get_general_variables = self.mock_get_general_variables
        xivo_recording_agi.get_campaigns = self.mock_get_campaigns

        self.instance_agi.set_variable = Mock()
        xivo_recording_agi.determinate_record()

        expected = [call('QR_RECORDQUEUE', '1'), call('__QR_CAMPAIGN_ID', self.xivo_campaign_id), call('__QR_BASE_FILENAME', self.base_filename)]

        print self.instance_agi.set_variable.mock_calls
        self.assertTrue(self.instance_agi.set_variable.mock_calls == expected)
