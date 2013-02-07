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
from sqlalchemy.exc import IntegrityError
from xivo_dao.helpers.cel_exception import InvalidInputException
from xivo_restapi.dao.exceptions import NoSuchElementException
from xivo_restapi.rest import rest_encoder
from xivo_restapi.restapi_config import RestAPIConfig
from xivo_restapi.services.agent_management import AgentManagement
from xivo_restapi.services.campagne_management import CampagneManagement
from xivo_restapi.services.queue_management import QueueManagement
from xivo_restapi.services.recording_management import RecordingManagement
import random
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
        self.instance_campagne_management.supplement_add_input\
                    .return_value = data

        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/', data = rest_encoder.encode(data))
        self.instance_campagne_management.supplement_add_input\
                    .assert_called_with(data)
        self.instance_campagne_management.create_campaign\
                    .assert_called_with(data)
        self.assertTrue(str(result.status).startswith(status)
                        and body == str(rest_encoder.decode(result.data)[0]),
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
        self.instance_campagne_management.supplement_add_input\
                    .return_value = data

        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/',
                              data = rest_encoder.encode(data))
        self.instance_campagne_management.supplement_add_input\
                    .assert_called_with(data)
        self.instance_campagne_management.create_campaign\
                    .assert_called_with(data)
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

        self.instance_campagne_management.get_campaigns_as_dict\
                    .return_value = data
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/?activated=true&campaign_name=test'
        result = self.app.get(url)

        args = {'campaign_name': 'test',
                'activated': 'true'}
        self.assertEqual(status, result.status)
        received_data = rest_encoder.decode(result.data\
                                            .replace("\\", "").strip('"'))
        self.assertTrue(received_data == data)
        self.instance_campagne_management.get_campaigns_as_dict\
                            .assert_called_with(args, False, {})

    def test_edit_campaign_success(self):
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
        self.instance_campagne_management.supplement_edit_input\
                    .return_value = data
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + str(campaign_id)
        result = self.app.put(url, data = rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.assertEqual(rest_encoder.decode(result.data), "Updated: True")
        self.instance_campagne_management.supplement_edit_input\
                    .assert_called_with(data)
        self.instance_campagne_management.update_campaign\
                    .assert_called_with(str(campaign_id), data)

    def test_edit_campaign_fail(self):
        status = "500 INTERNAL SERVER ERROR"

        campaign_id = random.randint(10000, 99999999)
        campagne_name = "campagne-" + str(campaign_id)

        data = {
            "campaign_name": campagne_name,
            "activated": False,
            "base_filename": campagne_name + "-",
            "queue_name": "queue_1"
        }

        self.instance_campagne_management.update_campaign.return_value = False
        self.instance_campagne_management.supplement_edit_input\
                    .return_value = data
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + str(campaign_id)
        result = self.app.put(url, data = rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.assertEqual(rest_encoder.decode(result.data)[0], "False")
        self.instance_campagne_management.supplement_edit_input\
                    .assert_called_with(data)
        self.instance_campagne_management.update_campaign\
                    .assert_called_with(str(campaign_id), data)

    def test_edit_campaign_no_such_element(self):
        status = "404 NOT FOUND"

        campaign_id = random.randint(10000, 99999999)
        campagne_name = "campagne-" + str(campaign_id)

        data = {
            "campaign_name": campagne_name,
            "activated": False,
            "base_filename": campagne_name + "-",
            "queue_name": "queue_1"
        }

        def mock_update(campaign_id, body):
            raise NoSuchElementException(str(campaign_id))

        self.instance_campagne_management.update_campaign\
                    .side_effect = mock_update
        self.instance_campagne_management.supplement_edit_input\
                    .return_value = data
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + str(campaign_id)
        result = self.app.put(url, data = rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.instance_campagne_management.supplement_edit_input\
                    .assert_called_with(data)
        self.instance_campagne_management.update_campaign\
                .assert_called_with(str(campaign_id), data)
        self.instance_campagne_management.update_campaign\
                .side_effect = None

    def test_edit_campaign_integrity_error(self):
        status = "400 BAD REQUEST"

        campaign_id = random.randint(10000, 99999999)
        campagne_name = "campagne-" + str(campaign_id)

        data = {
            "campaign_name": campagne_name,
            "activated": False,
            "base_filename": campagne_name + "-",
            "queue_name": "queue_1"
        }

        def mock_update(campaign_id, body):
            raise IntegrityError(None, None, None)

        self.instance_campagne_management.update_campaign\
                    .side_effect = mock_update
        self.instance_campagne_management.supplement_edit_input\
                    .return_value = data
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + str(campaign_id)
        result = self.app.put(url, data = rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.assertTrue(['duplicated_name'] == rest_encoder.decode(result.data))
        self.instance_campagne_management.supplement_edit_input\
                    .assert_called_with(data)
        self.instance_campagne_management.update_campaign\
                .assert_called_with(str(campaign_id), data)
        self.instance_campagne_management.update_campaign\
                .side_effect = None

    def test_edit_campaign_invalid_input(self):
        status = "400 BAD REQUEST"
        liste = ['un', 'deux', 'trois']
        campaign_id = random.randint(10000, 99999999)
        campagne_name = "campagne-" + str(campaign_id)

        data = {
            "campaign_name": campagne_name,
            "activated": False,
            "base_filename": campagne_name + "-",
            "queue_name": "queue_1"
        }

        def mock_update(campaign_id, body):
            raise InvalidInputException('', liste)

        self.instance_campagne_management.update_campaign\
                    .side_effect = mock_update
        self.instance_campagne_management.supplement_edit_input\
                    .return_value = data
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + str(campaign_id)
        result = self.app.put(url, data = rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.assertTrue(liste == rest_encoder.decode(result.data))
        self.instance_campagne_management.supplement_edit_input\
                    .assert_called_with(data)
        self.instance_campagne_management.update_campaign\
                .assert_called_with(str(campaign_id), data)
        self.instance_campagne_management.update_campaign\
                .side_effect = None

    def test_delete_integrity_error(self):
        campaign_id = str(random.randint(10000, 99999))
        status = '412 PRECONDITION FAILED'

        def mock_delete(campaign_id):
            raise IntegrityError(None, None, None)
        self.instance_campagne_management.delete\
                    .side_effect = mock_delete
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + campaign_id
        result = self.app.delete(url, '')
        self.assertEqual(result.status, status)
        self.assertEqual(rest_encoder.decode(result.data),
                         ["campaign_not_empty"])

    def test_delete_no_such_element(self):
        campaign_id = str(random.randint(10000, 99999))
        status = '404 NOT FOUND'

        def mock_delete(campaign_id):
            raise NoSuchElementException("")
        self.instance_campagne_management.delete\
                    .side_effect = mock_delete
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + campaign_id
        result = self.app.delete(url, '')
        self.assertEqual(result.status, status)
        self.assertEqual(rest_encoder.decode(result.data),
                         ["campaign_not_found"])

    def test_delete_success(self):
        campaign_id = str(random.randint(10000, 99999))
        status = '200 OK'

        self.instance_campagne_management.delete = Mock()
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + campaign_id
        result = self.app.delete(url, '')
        self.assertEqual(result.status, status)
