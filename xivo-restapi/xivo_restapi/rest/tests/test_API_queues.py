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
from xivo_restapi.rest import rest_encoder
from xivo_restapi.restapi_config import RestAPIConfig
from xivo_restapi.services.agent_management import AgentManagement
from xivo_restapi.services.campagne_management import CampagneManagement
from xivo_restapi.services.queue_management import QueueManagement
from xivo_restapi.services.recording_management import RecordingManagement
import unittest

mock_agent_management = Mock(AgentManagement)
mock_campaign_management = Mock(CampagneManagement)
mock_recording_management = Mock(RecordingManagement)
mock_queue_management = Mock(QueueManagement)


class TestFlaskHttpRoot(unittest.TestCase):

    def setUp(self):

        self.patcher_agent = patch("xivo_restapi.services." + \
                             "agent_management.AgentManagement")
        mock_agent = self.patcher_agent.start()
        self.instance_agent_management = mock_agent_management
        mock_agent.return_value = self.instance_agent_management

        self.patcher_queue = patch("xivo_restapi.services." + \
                             "queue_management.QueueManagement")
        mock_queue = self.patcher_queue.start()
        self.instance_queue_management = mock_queue_management
        mock_queue.return_value = self.instance_queue_management

        self.patcher_recording = patch("xivo_restapi.services." + \
                             "recording_management.RecordingManagement")
        mock_recording = self.patcher_recording.start()
        self.instance_recording_management = mock_recording_management
        mock_recording.return_value = self.instance_recording_management

        self.patcher_campaign = patch("xivo_restapi.services." + \
                             "campagne_management.CampagneManagement")
        mock_campaign = self.patcher_campaign.start()
        self.instance_campagne_management = mock_campaign_management
        mock_campaign.return_value = self.instance_campagne_management

        from xivo_restapi.rest import flask_http_server
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    def tearDown(self):
        self.patcher_recording.stop()
        self.patcher_agent.stop()
        self.patcher_campaign.stop()
        self.patcher_queue.stop()

    def test_list_queues(self):
        status = "200 OK"
        liste = [{"number": "1"},
                 {"number": "3"},
                 {"number": "2"}]
        self.instance_queue_management.get_all_queues\
                    .return_value = liste
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_QUEUES_SERVICE_PATH + '/',
                              '')

        self.instance_queue_management.get_all_queues\
                    .assert_any_call()
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)
        liste = sorted(liste, key=lambda k: k['number'])
        self.assertTrue(liste == rest_encoder.decode(result.data),
                             "Result is not the expected one: "\
                                + str(result.data))

    def test_list_queues_error(self):
        status = "500 INTERNAL SERVER ERROR"

        def mock_get_all_queues():
            raise Exception()

        self.instance_queue_management.get_all_queues\
                    .side_effect = mock_get_all_queues
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_QUEUES_SERVICE_PATH + '/',
                              '')

        self.instance_queue_management.get_all_queues\
                    .assert_any_call()
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)
        self.instance_queue_management.get_all_queues\
                    .side_effect = None
