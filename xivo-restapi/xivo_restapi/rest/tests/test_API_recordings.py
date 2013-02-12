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
from xivo_dao.alchemy.recordings import Recordings
from xivo_restapi.rest import rest_encoder
from xivo_restapi.rest.helpers import recordings_helper
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

    def test_add_recording_fail(self):
        status = "500 INTERNAL SERVER ERROR"
        campaign_id = '1'
        cid = '001'
        agent_id = '1'
        data = {
            "cid": cid,
            'campaign_id': campaign_id,
            "agent_id": agent_id
        }
        self.instance_recording_management.add_recording.return_value = False
        recordings_helper.supplement_add_input = Mock()
        recordings_helper.supplement_add_input.return_value = data
        recordings_helper.create_instance = Mock()
        recording = Recordings()
        recordings_helper.create_instance.return_value = recording

        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/' + campaign_id + '/',
                              data=rest_encoder.encode(data))
        recordings_helper.supplement_add_input.assert_called_with(data)
        recordings_helper.create_instance.assert_called_with(data)
        self.instance_recording_management.add_recording\
                    .assert_called_with(campaign_id, recording)
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)

    def test_add_recording_success(self):
        status = "201 CREATED"
        campaign_id = '1'
        cid = '001'
        agent_id = '1'
        data = {
            "cid": cid,
            'campaign_id': campaign_id,
            "agent_id": agent_id
        }

        self.instance_recording_management.add_recording.return_value = True
        recordings_helper.supplement_add_input.return_value = data
        recordings_helper.create_instance = Mock()
        recording = Recordings()
        recordings_helper.create_instance.return_value = recording

        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/' + campaign_id + '/',
                              data=rest_encoder.encode(data))
        recordings_helper.supplement_add_input.assert_called_with(data)
        recordings_helper.create_instance.assert_called_with(data)
        self.instance_recording_management.add_recording\
                    .assert_called_with(campaign_id, recording)
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)

    def test_add_recording_client_error(self):
        status = "400 BAD REQUEST"
        campaign_id = '1'
        cid = '001'
        agent_id = '1'
        data = {
            "cid": cid,
            'campaign_id': campaign_id,
            "agent_id": agent_id
        }

        def mock_add_recording(campaign_id, data):
            raise Exception()

        self.instance_recording_management.add_recording\
                .side_effect = mock_add_recording
        recordings_helper.supplement_add_input = Mock()
        recordings_helper.supplement_add_input.return_value = data
        recordings_helper.create_instance = Mock()
        recording = Recordings()
        recordings_helper.create_instance.return_value = recording

        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/' + campaign_id + '/',
                              data=rest_encoder.encode(data))
        recordings_helper.supplement_add_input.assert_called_with(data)
        recordings_helper.create_instance.assert_called_with(data)
        self.instance_recording_management.add_recording\
                    .assert_called_with(campaign_id, recording)
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)
        self.instance_recording_management.add_recording.side_effect = None

    def test_list_recording_success(self):
        status = "200 OK"
        campaign_id = '1'
        obj = Recordings()
        data = (1, [obj])
        self.instance_recording_management.get_recordings.return_value = data
        params = "?_page=1&_pagesize=20&foo=bar"
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/' + campaign_id + '/' + params,
                              '')
        self.instance_recording_management.get_recordings\
                    .assert_called_with(campaign_id,
                                        {"foo": "bar"},
                                        (1, 20))
        self.assertEquals(result.status, status)
        expected_result = rest_encoder.encode({'total': 1,
                          'data': [obj.todict()]})
        self.assertEqual(expected_result, result.data)

    def test_list_recording_fail(self):
        status = "500 INTERNAL SERVER ERROR"
        campaign_id = '1'

        def mock_get_recordings(campaign, params, technical_params):
            raise Exception

        self.instance_recording_management.get_recordings.side_effect = mock_get_recordings
        params = "?_page=1&_pagesize=20&foo=bar"
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/' + campaign_id + '/' + params,
                              '')
        self.instance_recording_management.get_recordings\
                    .assert_called_with(campaign_id,
                                        {"foo": "bar"},
                                        (1, 20))
        self.assertEquals(result.status, status)
        self.instance_recording_management.get_recordings\
            .side_effect = None

    def test_search(self):
        status = "200 OK"
        campaign_id = '1'

        self.instance_recording_management.search_recordings\
            .return_value = True
        params = "?_page=1&_pagesize=20&foo=bar"
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/' + campaign_id + '/search' + params,
                              '')
        self.instance_recording_management.search_recordings\
                    .assert_called_with(campaign_id,
                                        {"foo": "bar"},
                                        (1, 20))
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)

    def test_search_fail(self):
        status = "500 INTERNAL SERVER ERROR"
        campaign_id = '1'

        def mock_search(campaign, params, technical):
            raise Exception()

        self.instance_recording_management.search_recordings\
            .side_effect = mock_search
        params = "?_page=1&_pagesize=20&foo=bar"
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/' + campaign_id + '/search' + params,
                              '')
        self.instance_recording_management.search_recordings\
                    .assert_called_with(campaign_id,
                                        {"foo": "bar"},
                                        (1, 20))
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)
        self.instance_recording_management.search_recordings\
            .side_effect = None

    def test_delete(self):
        status = "200 OK"
        campaign_id = '1'
        recording_id = '001'

        self.instance_recording_management.delete\
            .return_value = True
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/' + campaign_id + '/' + recording_id,
                              '')
        self.instance_recording_management.delete\
                    .assert_called_with(campaign_id,
                                        recording_id)
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)

    def test_delete_not_found(self):
        status = "404 NOT FOUND"
        campaign_id = '1'
        recording_id = '001'

        self.instance_recording_management.delete\
            .return_value = False
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/' + campaign_id + '/' + recording_id,
                              '')
        self.instance_recording_management.delete\
                    .assert_called_with(campaign_id,
                                        recording_id)
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)

    def test_delete_error(self):
        status = "500 INTERNAL SERVER ERROR"
        campaign_id = '1'
        recording_id = '001'

        def mock_delete(campaign_id, recording_id):
            raise Exception()

        self.instance_recording_management.delete\
            .side_effect = mock_delete
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/' + campaign_id + '/' + recording_id,
                              '')
        self.instance_recording_management.delete\
                    .assert_called_with(campaign_id,
                                        recording_id)
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status:" +
                        result.status)
        self.instance_recording_management.delete\
            .side_effect = None
