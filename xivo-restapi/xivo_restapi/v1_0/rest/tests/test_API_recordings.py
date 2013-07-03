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


import unittest

from mock import Mock, patch
from xivo_dao.alchemy.recordings import Recordings
from xivo_restapi import flask_http_server
from xivo_restapi.v1_0 import rest_encoder
from xivo_restapi.v1_0.rest.helpers.recordings_helper import RecordingsHelper
from xivo_restapi.v1_0.restapi_config import RestAPIConfig
from xivo_restapi.v1_0.services.recording_management import RecordingManagement
from xivo_restapi.v1_0.services.utils.exceptions import InvalidInputException

BASE_URL = "%s%s" % (RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH, RestAPIConfig.XIVO_RECORDING_SERVICE_PATH)


class TestAPIRecordings(unittest.TestCase):

    def setUp(self):

        self.patcher_recordings = patch("xivo_restapi.v1_0.rest.API_recordings.RecordingManagement")
        mock_recording = self.patcher_recordings.start()
        self.instance_recording_management = Mock(RecordingManagement)
        mock_recording.return_value = self.instance_recording_management

        self.patcher_recordings_helper = patch("xivo_restapi.v1_0.rest.API_recordings.RecordingsHelper")
        mock_recordings_helper = self.patcher_recordings_helper.start()
        self.instance_recordings_helper = Mock(RecordingsHelper)
        mock_recordings_helper.return_value = self.instance_recordings_helper

        flask_http_server.register_blueprints()
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    def tearDown(self):
        self.patcher_recordings.stop()
        self.patcher_recordings_helper.stop()

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
        self.instance_recordings_helper.supplement_add_input = Mock()
        self.instance_recordings_helper.supplement_add_input.return_value = data
        self.instance_recordings_helper.create_instance = Mock()
        recording = Recordings()
        self.instance_recordings_helper.create_instance.return_value = recording

        result = self.app.post("%s/%s/" % (BASE_URL, campaign_id), data=rest_encoder.encode(data))

        self.instance_recordings_helper.supplement_add_input.assert_called_with(data)
        self.instance_recordings_helper.create_instance.assert_called_with(data)
        self.instance_recording_management.add_recording.assert_called_with(int(campaign_id), recording)
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status: %s" % result.status)

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
        self.instance_recordings_helper.supplement_add_input.return_value = data
        self.instance_recordings_helper.create_instance = Mock()
        recording = Recordings()
        self.instance_recordings_helper.create_instance.return_value = recording

        result = self.app.post("%s/%s/" % (BASE_URL, campaign_id), data=rest_encoder.encode(data))

        self.instance_recordings_helper.supplement_add_input.assert_called_with(data)
        self.instance_recordings_helper.create_instance.assert_called_with(data)
        self.instance_recording_management.add_recording.assert_called_with(int(campaign_id), recording)
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status: %s" % result.status)

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

        self.instance_recording_management.add_recording.side_effect = InvalidInputException('', ['my error'])
        self.instance_recordings_helper.supplement_add_input = Mock()
        self.instance_recordings_helper.supplement_add_input.return_value = data
        self.instance_recordings_helper.create_instance = Mock()
        recording = Recordings()
        self.instance_recordings_helper.create_instance.return_value = recording

        result = self.app.post("%s/%s/" % (BASE_URL, campaign_id), data=rest_encoder.encode(data))

        self.instance_recordings_helper.supplement_add_input.assert_called_with(data)
        self.instance_recordings_helper.create_instance.assert_called_with(data)
        self.instance_recording_management.add_recording.assert_called_with(int(campaign_id), recording)
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status: %s" % result.status)

        self.instance_recording_management.add_recording.side_effect = None

    def test_list_recording_success(self):
        status = "200 OK"
        campaign_id = '1'
        obj = Recordings()
        data = (1, [obj])
        self.instance_recording_management.get_recordings.return_value = data

        url = "%s/%s/?_page=1&_pagesize=20&foo=bar" % (BASE_URL, campaign_id)
        result = self.app.get(url, '')

        self.instance_recording_management.get_recordings.assert_called_with(
            campaign_id,
            {"foo": "bar"},
            (1, 20))
        self.assertEquals(result.status, status)

        expected_result = rest_encoder.encode({'total': 1,
                                               'items': [obj.todict()]})
        self.assertEqual(expected_result, result.data)

    def test_list_recording_fail(self):
        status = "500 INTERNAL SERVER ERROR"
        campaign_id = '1'
        self.instance_recording_management.get_recordings.side_effect = Exception

        url = "%s/%s/?_page=1&_pagesize=20&foo=bar" % (BASE_URL, campaign_id)
        result = self.app.get(url, '')

        self.instance_recording_management.get_recordings.assert_called_with(
            campaign_id,
            {"foo": "bar"},
            (1, 20))
        self.assertEquals(result.status, status)
        self.instance_recording_management.get_recordings.side_effect = None

    def test_search(self):
        status = "200 OK"
        campaign_id = '1'

        self.instance_recording_management.search_recordings.return_value = True

        url = "%s/%s/search?_page=1&_pagesize=20&foo=bar" % (BASE_URL, campaign_id)
        result = self.app.get(url, '')

        self.instance_recording_management.search_recordings.assert_called_with(
            campaign_id,
            {"foo": "bar"},
            (1, 20))
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status: %s" % result.status)

    def test_search_fail(self):
        status = "500 INTERNAL SERVER ERROR"
        campaign_id = '1'

        self.instance_recording_management.search_recordings.side_effect = Exception

        url = "%s/%s/search?_page=1&_pagesize=20&foo=bar" % (BASE_URL, campaign_id)
        result = self.app.get(url, '')

        self.instance_recording_management.search_recordings.assert_called_with(
            campaign_id,
            {"foo": "bar"},
            (1, 20))
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status: %s" % result.status)
        self.instance_recording_management.search_recordings.side_effect = None

    def test_delete(self):
        status = "200 OK"
        campaign_id = '1'
        recording_id = '001'

        self.instance_recording_management.delete.return_value = True

        url = "%s/%s/%s" % (BASE_URL, campaign_id, recording_id)
        result = self.app.delete(url, '')

        self.instance_recording_management.delete.assert_called_with(
            int(campaign_id),
            recording_id)
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status: %s" % result.status)

    def test_delete_not_found(self):
        status = "404 NOT FOUND"
        campaign_id = '1'
        recording_id = '001'

        self.instance_recording_management.delete.return_value = False

        url = "%s/%s/%s" % (BASE_URL, campaign_id, recording_id)
        result = self.app.delete(url, '')

        self.instance_recording_management.delete.assert_called_with(
            int(campaign_id),
            recording_id)
        self.assertTrue(result.status == status,
                        "Status comparison failed, received status: %s" % result.status)

    def test_delete_error(self):
        status = "500 INTERNAL SERVER ERROR"
        campaign_id = '1'
        recording_id = '001'
        self.instance_recording_management.delete.side_effect = Exception

        url = "%s/%s/%s" % (BASE_URL, campaign_id, recording_id)
        result = self.app.delete(url, '')

        self.instance_recording_management.delete.assert_called_with(
            int(campaign_id),
            recording_id)

        self.assertTrue(result.status == status,
                        "Status comparison failed, received status: %s" % result.status)

        self.instance_recording_management.delete.side_effect = None
