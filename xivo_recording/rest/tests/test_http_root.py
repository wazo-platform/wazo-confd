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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..


from mock import Mock, patch
from urlparse import urlparse, parse_qs
from xivo_recording.recording_config import RecordingConfig
from xivo_recording.rest import rest_encoder
from xivo_recording.services.campagne_management import CampagneManagement
import random
import unittest

mock_campagne_management = Mock(CampagneManagement)


class TestFlaskHttpRoot(unittest.TestCase):

    def setUp(self):

        self.patcher = patch("xivo_recording.services.campagne_management.CampagneManagement")

        mock = self.patcher.start()
        self.instance_campagne_management = mock_campagne_management
        mock.return_value = self.instance_campagne_management

        from xivo_recording.rest import flask_http_server
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    def tearDown(self):
        self.patcher.stop()

    def test_add_campaign_fail(self):
        status = "500 INTERNAL SERVER ERROR"
        body = "error to fail the test"

        unique_id = str(random.randint(10000, 99999999))
        campagne_name = "campagne-" + unique_id

        data = {
            "campaign_name": campagne_name,
            "activated": False,
            "base_filename": campagne_name + "-",
            "queue_name": "queue_1"
        }

        self.instance_campagne_management.create_campaign.return_value = body
        self.instance_campagne_management.supplement_add_input.return_value = data
        
        result = self.app.post(RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RecordingConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/', data=rest_encoder.encode(data))
        print "result add campaign: " + result.data
        self.instance_campagne_management.supplement_add_input.assert_called_with(data)
        self.instance_campagne_management.create_campaign.assert_called_with(data)
        self.assertTrue(str(result.status).startswith(status)
                        and body == str(result.data).strip('"'),
                        "Status comparison failed, received status:" +
                        result.status + ", data: " + result.data)

    def test_add_campaign_success(self):
        status = "201 CREATED"

        unique_id = str(random.randint(10000, 99999999))
        campagne_name = "campagne-" + unique_id

        data = {
            "campaign_name": campagne_name,
            "activated": False,
            "base_filename": campagne_name + "-",
            "queue_name": "queue_1"
        }

        self.instance_campagne_management.create_campaign.return_value = 1
        self.instance_campagne_management.supplement_add_input.return_value = data

        result = self.app.post(RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RecordingConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/',
                              data=rest_encoder.encode(data))
        self.instance_campagne_management.supplement_add_input.assert_called_with(data)
        self.instance_campagne_management.create_campaign.assert_called_with(data)
        self.assertTrue(str(result.status).startswith(status),
                        "Status comparison failed, received status:" +
                        result.status + ", data: " + result.data)

    def test_get_campaigns(self):
        status = "200 OK"

        unique_id = str(random.randint(10000, 99999999))
        campagne_name = "campagne-" + unique_id

        data = {
            "campign_name": campagne_name,
            "activated": False,
            "base_filename": campagne_name + "-",
            "queue_name": "queue_1"
        }

        self.instance_campagne_management.get_campaigns_as_dict.return_value = data
        url = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RecordingConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/?activated=true&campaign_name=test'
        result = self.app.get(url)

        args = {'campaign_name' : 'test',
                'activated' : 'true'}
        print "args: " + str(args)
        self.assertEqual(status, result.status)
        received_data = rest_encoder.decode(result.data.replace("\\", "").strip('"'))
        self.assertDictEqual(received_data, data)
        self.instance_campagne_management.get_campaigns_as_dict.assert_called_with(args, False, {})

    def test_edit_campaign(self):
        status = "200 OK"

        campaign_id = random.randint(10000, 99999999)
        campagne_name = "campagne-" + str(campaign_id)

        data = {
            "campaign_name": campagne_name,
            "activated": False,
            "base_filename": campagne_name + "-",
            "queue_name": "queue_1"
        }

        self.instance_campagne_management.update_campaign.return_value = True
        self.instance_campagne_management.supplement_edit_input.return_value = data
        url = RecordingConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RecordingConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + str(campaign_id)
        result = self.app.put(url, data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.assertEqual(result.data, "Updated: True")
        self.instance_campagne_management.supplement_edit_input.assert_called_with(data)
        self.instance_campagne_management.update_campaign.assert_called_with(str(campaign_id), data)