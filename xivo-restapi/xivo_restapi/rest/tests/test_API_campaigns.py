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
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_restapi.rest import rest_encoder
from xivo_restapi.rest.helpers.campaigns_helper import CampaignsHelper
from xivo_restapi.restapi_config import RestAPIConfig
from xivo_restapi.services.campagne_management import CampagneManagement
from xivo_restapi.services.utils.exceptions import NoSuchElementException, \
    InvalidInputException
import random
import unittest


class TestAPICampaigns(unittest.TestCase):

    def setUp(self):
        self.patcher_campaigns = patch("xivo_restapi.rest." + \
                                     "API_campaigns.CampagneManagement")
        mock_campaign = self.patcher_campaigns.start()
        self.instance_campaign_management = Mock(CampagneManagement)
        mock_campaign.return_value = self.instance_campaign_management

        self.patch_campaigns_helper = patch("xivo_restapi.rest." + \
                                     "API_campaigns.CampaignsHelper")
        mock_campaigns_helper = self.patch_campaigns_helper.start()
        self.instance_campaigns_helper = Mock(CampaignsHelper)
        mock_campaigns_helper.return_value = self.instance_campaigns_helper
        from xivo_restapi.rest import flask_http_server
        flask_http_server.register_blueprints()
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    def tearDown(self):
        self.patch_campaigns_helper.stop()
        self.patcher_campaigns.stop()

    def test_add_campaign_fail(self):
        status = "500 INTERNAL SERVER ERROR"
        body = "error to fail the test"

        unique_id = str(random.randint(10000, 99999999))
        campagne_name = "campagne-" + unique_id

        data_dict = {
            "campaign_name": campagne_name,
            "activated": False,
            "base_filename": campagne_name + "-",
            "queue_name": "queue_1"
        }
        self.instance_campaigns_helper.create_instance = Mock()
        campaign = RecordCampaigns()
        self.instance_campaigns_helper.create_instance.return_value = campaign

        self.instance_campaign_management.create_campaign = Mock()
        self.instance_campaign_management.create_campaign.return_value = body
        self.instance_campaigns_helper.supplement_add_input = Mock()
        self.instance_campaigns_helper.supplement_add_input.return_value = data_dict

        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/', data=rest_encoder.encode(data_dict))

        self.instance_campaigns_helper.supplement_add_input.assert_called_with(data_dict)  #@UndefinedVariable
        self.instance_campaigns_helper.create_instance.assert_called_with(data_dict)  #@UndefinedVariable
        self.instance_campaign_management.create_campaign\
                    .assert_called_with(campaign)
        self.assertTrue(str(result.status).startswith(status))
        self.assertEqual(body, str(rest_encoder.decode(result.data)[0]))

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

        self.instance_campaign_management.create_campaign.return_value = 1
        self.instance_campaigns_helper.supplement_add_input = Mock()
        self.instance_campaigns_helper.supplement_add_input\
                    .return_value = data
        self.instance_campaigns_helper.create_instance = Mock()
        campaign = RecordCampaigns()
        self.instance_campaigns_helper.create_instance.return_value = campaign

        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_RECORDING_SERVICE_PATH +
                              '/',
                              data=rest_encoder.encode(data))
        self.instance_campaigns_helper.supplement_add_input.assert_called_with(data)  #@UndefinedVariable
        self.instance_campaign_management.create_campaign\
                    .assert_called_with(campaign)
        self.assertTrue(str(result.status).startswith(status),
                        "Status comparison failed, received status:" +
                        result.status + ", data: " + result.data)

    def test_get_campaigns(self):
        campaign = RecordCampaigns()
        campaign.campaign_name = 'campagne'
        campaign.activated = False
        campaign.base_filename = "file-"
        campaign.queue_name = 'queue_1'

        status = "200 OK"
        data = {'total': 1,
                'items': [rest_encoder._serialize(campaign)]}

        self.instance_campaign_management.get_campaigns.return_value = (1, [campaign])

        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/?activated=true&campaign_name=test'
        result = self.app.get(url)

        args = {'campaign_name': 'test',
                'activated': 'true'}
        self.assertEqual(status, result.status)
        self.assertEquals(result.data, rest_encoder.encode(data))
        self.instance_campaign_management.get_campaigns\
                            .assert_called_with(args, False, (0, 0))

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

        self.instance_campaign_management.update_campaign.return_value = True
        self.instance_campaigns_helper.supplement_edit_input = Mock()
        self.instance_campaigns_helper.supplement_edit_input\
                    .return_value = data
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + str(campaign_id)
        result = self.app.put(url, data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.assertEqual(rest_encoder.decode(result.data), "Updated: True")
        self.instance_campaigns_helper.supplement_edit_input.assert_called_with(data)  #@UndefinedVariable
        self.instance_campaign_management.update_campaign\
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

        self.instance_campaign_management.update_campaign.return_value = False
        self.instance_campaigns_helper.supplement_edit_input = Mock()
        self.instance_campaigns_helper.supplement_edit_input.return_value = data
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + str(campaign_id)
        result = self.app.put(url, data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.assertEqual(rest_encoder.decode(result.data)[0], "False")
        self.instance_campaigns_helper.supplement_edit_input\
                    .assert_called_with(data)  #@UndefinedVariable
        self.instance_campaign_management.update_campaign\
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

        self.instance_campaign_management.update_campaign.side_effect = NoSuchElementException('1')
        self.instance_campaigns_helper.supplement_edit_input = Mock()
        self.instance_campaigns_helper.supplement_edit_input.return_value = data
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + str(campaign_id)
        result = self.app.put(url, data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.instance_campaigns_helper.supplement_edit_input.assert_called_with(data)  #@UndefinedVariable
        self.instance_campaign_management.update_campaign\
                .assert_called_with(str(campaign_id), data)
        self.instance_campaign_management.update_campaign\
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

        self.instance_campaign_management.update_campaign\
                    .side_effect = IntegrityError(None, None, None)
        self.instance_campaigns_helper.supplement_edit_input = Mock()
        self.instance_campaigns_helper.supplement_edit_input.return_value = data
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + str(campaign_id)
        result = self.app.put(url, data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.assertTrue(['duplicated_name'] == rest_encoder.decode(result.data))
        self.instance_campaigns_helper.supplement_edit_input.assert_called_with(data)  #@UndefinedVariable
        self.instance_campaign_management.update_campaign\
                .assert_called_with(str(campaign_id), data)
        self.instance_campaign_management.update_campaign\
                .side_effect = None

    def test_edit_campaign_invalid_input(self):
        status = "400 BAD REQUEST"
        my_list = ['un', 'deux', 'trois']
        campaign_id = random.randint(10000, 99999999)
        campagne_name = "campagne-" + str(campaign_id)

        data = {
            "campaign_name": campagne_name,
            "activated": False,
            "base_filename": campagne_name + "-",
            "queue_name": "queue_1"
        }

        self.instance_campaign_management.update_campaign\
                    .side_effect = InvalidInputException('', my_list)
        self.instance_campaigns_helper.supplement_edit_input = Mock()
        self.instance_campaigns_helper.supplement_edit_input.return_value = data
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + str(campaign_id)
        result = self.app.put(url, data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.assertTrue(my_list == rest_encoder.decode(result.data))
        self.instance_campaigns_helper.supplement_edit_input.assert_called_with(data)  #@UndefinedVariable
        self.instance_campaign_management.update_campaign\
                .assert_called_with(str(campaign_id), data)
        self.instance_campaign_management.update_campaign\
                .side_effect = None

    def test_delete_integrity_error(self):
        campaign_id = str(random.randint(10000, 99999))
        status = '412 PRECONDITION FAILED'
        self.instance_campaign_management.delete\
                    .side_effect = IntegrityError(None, None, None)
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
        self.instance_campaign_management.delete\
                    .side_effect = NoSuchElementException("")
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + campaign_id
        result = self.app.delete(url, '')
        self.assertEqual(result.status, status)

    def test_delete_success(self):
        campaign_id = str(random.randint(10000, 99999))
        status = '200 OK'

        self.instance_campaign_management.delete = Mock()
        url = RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH + \
                RestAPIConfig.XIVO_RECORDING_SERVICE_PATH + \
                '/' + campaign_id
        result = self.app.delete(url, '')
        self.assertEqual(result.status, status)
