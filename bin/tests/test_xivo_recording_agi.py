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

from gevent.httplib import HTTPConnection
from mock import Mock, patch, call
from xivo.agi import AGI
from xivo_recording.recording_config import RecordingConfig
from xivo_recording.rest import rest_encoder
import random
import sys
import unittest
mock_agi = Mock(AGI)
mock_http_connection = Mock(HTTPConnection)
mock_sys = Mock(sys)


class TestXivoRecordingAgi(unittest.TestCase):

    def setUp(self):
        self.xivo_queue_name = 'xivo_name'
        self.xivo_queue_id = 1
        self.xivo_campaign_id = 1
        self.xivo_srcnum = '2345'
        self.xivo_destnum = '1001'
        self.base_filename = 'filename'
        self.base_filename = 'base_filename' + str(random.randint(100, 999))
        self.rest_response = '[{"base_filename": "' + self.base_filename +\
             '", "queue_name": "queue_1", "activated": "True",' +\
              ' "campaign_name": "test"}]'
        self.xivo_date = '2012-01-01 00:00:00'
        self.unique_id = '001'
        self.agent_no = '1111'
        self.caller_no = '2222'
        self.xivo_client_id = 'abc'

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
        self.instance_agi.get_variable.side_effect = self.mock_agi_get_variable
        self.instance_agi.get_variable.call_args_list = []
        xivo_vars = {'queue_name': self.xivo_queue_name,
                     'xivo_srcnum': self.xivo_srcnum,
                     'xivo_dstnum': self.xivo_destnum}
        expected = [call('XIVO_QUEUENAME'), call('XIVO_SRCNUM'), call('XIVO_DSTNUM')]
        from bin import xivo_recording_agi
        res = xivo_recording_agi.get_general_variables()
        self.assertDictEqual(res, xivo_vars)
        self.assertListEqual(expected, self.instance_agi.get_variable.call_args_list,
                             "Actual calls: " + str(self.instance_agi.get_variable.call_args_list) + \
                             ", expected were: " + str(expected))

    def test_xivo_recording_agi_get_detailed_variables(self):
        self.instance_agi.get_variable.side_effect = self.mock_agi_get_variable
        self.instance_agi.get_variable.call_args_list = []
        from bin import xivo_recording_agi
        res = xivo_recording_agi.get_detailed_variables()
        expected_calls = [call('QR_CAMPAIGN_ID'), call('QR_AGENT_NB'), 
                          call('QR_CALLER_NB'), call('QR_TIME'),
                          call('UNIQUEID'), call('QR_QUEUENAME'),
                          call(RecordingConfig.XIVO_DIALPLAN_RECORDING_USERDATA_VAR_NAME)]
        xivo_vars = {'campaign_id': str(self.xivo_campaign_id),
                     'agent_no': self.agent_no,
                     'caller': self.caller_no,
                     'start_time': self.xivo_date,
                     'cid': self.unique_id,
                     'queue_name': self.xivo_queue_name,
                     'client_id': self.xivo_client_id}
        self.assertDictEqual(res, xivo_vars)
        self.assertListEqual(expected_calls, self.instance_agi.get_variable.call_args_list)

    def test_xivo_recording_agi_get_campaigns(self):
        response = Mock()
        response.read.return_value = self.rest_response
        response.status = 200

        self.instance_http_connection.getresponse.return_value = response

        self.instance_agi.set_variable.return_value = 0
        from bin import xivo_recording_agi
        xivo_recording_agi.get_campaigns(self.xivo_queue_id)

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH +\
                        RecordingConfig.XIVO_RECORDING_SERVICE_PATH +\
                        '/?activated=true&queue_id=' + str(self.xivo_queue_id) +\
                        '&running=true'
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE

        self.instance_http_connection.request.assert_called_with("GET",
                                                     requestURI, None, headers)

    def mock_get_general_variables(self):
        xivo_vars = {}
        xivo_vars['queue_name'] = self.xivo_queue_name
        xivo_vars['xivo_srcnum'] = self.xivo_srcnum
        xivo_vars['xivo_dstnum'] = self.xivo_destnum
        return xivo_vars

    def mock_get_queue_id(self, name):
        if(name == self.xivo_queue_name):
            return self.xivo_queue_id
        else:
            raise Exception

    def mock_get_campaigns(self, queue_id):
        if(queue_id == self.xivo_queue_id):
            return rest_encoder.encode({
                            'data': [{'id': self.xivo_campaign_id,
                                      'activated': "True"}]
                            })
        else:
            raise Exception

    def mock_agi_get_variable(self, name):
        if name == 'QR_TIME':
            return self.xivo_date
        elif name == 'QR_CAMPAIGN_ID':
            return str(self.xivo_campaign_id)
        elif name == 'UNIQUEID':
            return self.unique_id
        elif name == RecordingConfig.XIVO_DIALPLAN_CLIENTFIELD:
            return self.xivo_client_id
        elif name == 'XIVO_DSTNUM':
            return self.xivo_destnum
        elif name == 'XIVO_QUEUENAME':
            return self.xivo_queue_name
        elif name == 'XIVO_SRCNUM':
            return self.xivo_srcnum
        elif name == 'QR_AGENT_NB':
            return self.agent_no
        elif name == 'QR_CALLER_NB':
            return self.caller_no
        elif name == 'QR_QUEUENAME':
            return self.xivo_queue_name
        elif name == RecordingConfig.XIVO_DIALPLAN_RECORDING_USERDATA_VAR_NAME:
            return self.xivo_client_id

    def test_xivo_recording_set_user_field(self):
        expected_user_data = 'test'
        self.instance_agi.get_variable.return_value = expected_user_data

        from bin import xivo_recording_agi
        xivo_recording_agi.set_user_field()

        self.instance_agi.get_variable.assert_called_with(RecordingConfig.XIVO_DIALPLAN_CLIENTFIELD)
        self.instance_agi.set_variable.assert_called_with('__' + RecordingConfig.XIVO_DIALPLAN_RECORDING_USERDATA_VAR_NAME,
                                                          expected_user_data)

    def test_xivo_recording_determinate_record(self):

        expected_data = 'test'

        from bin import xivo_recording_agi
        xivo_recording_agi.get_queue_id = self.mock_get_queue_id
        xivo_recording_agi.get_general_variables = self.mock_get_general_variables
        xivo_recording_agi.get_campaigns = self.mock_get_campaigns

        self.instance_agi.set_variable = Mock()
        self.instance_agi.get_variable = Mock()
        self.instance_agi.get_variable.return_value = expected_data
        xivo_recording_agi.determinate_record()

        expected = [call('QR_RECORDQUEUE', '1'),
                    call('__QR_CAMPAIGN_ID', self.xivo_campaign_id),
                    call('__' + RecordingConfig.XIVO_DIALPLAN_RECORDING_USERDATA_VAR_NAME, expected_data)]
        print(self.instance_agi.set_variable.mock_calls)
        self.assertTrue(self.instance_agi.set_variable.mock_calls == expected)

    def test_process_call_hangup(self):

        response = Mock()
        response.read.return_value = 'Updated: True'
        response.status = 200
        self.instance_http_connection.getresponse.return_value = response

        from bin import xivo_recording_agi

        with self.assertRaises(SystemExit):
            xivo_recording_agi.process_call_hangup(self.unique_id, str(self.xivo_campaign_id), self.xivo_date)

        requestURI = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                    RecordingConfig.XIVO_RECORDING_SERVICE_PATH + "/1/001"
        body = {"end_time": '2012-01-01 00:00:00'}
        headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
        self.instance_http_connection.request\
                .assert_called_with("PUT", requestURI,
                                    rest_encoder.encode(body), headers)

