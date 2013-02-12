# -*- coding: UTF-8 -*-
#
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

from datetime import datetime
from mock import Mock, patch
from sqlalchemy.exc import IntegrityError
from xivo_dao import queue_dao, record_campaigns_dao
from xivo_dao.alchemy.record_campaigns import RecordCampaigns
from xivo_restapi.services.utils.exceptions import NoSuchElementException, \
    InvalidInputException
import copy
import unittest


class TestCampagneManagement(unittest.TestCase):

    def setUp(self):
        self.queue_name = 'queuename'
        self.queue_display_name = "queuedisplayname"
        self.queue_number = '1000'

        from xivo_restapi.services.campagne_management import CampagneManagement
        self._campagneManager = CampagneManagement()
        queue_dao.id_from_name = Mock(return_value='1')
        queue_dao.queue_name = Mock(return_value=self.queue_name)
        queue_dao.get_display_name_number = Mock(
                                  return_value=(self.queue_display_name,
                                                self.queue_number))
        self._create_sample_campaign()

    def test_create_campaign(self):
        campaign = copy.deepcopy(self.sample_campaign)
        record_campaigns_dao.add_or_update = Mock()
        record_campaigns_dao.add_or_update.return_value = 1
        self._campagneManager._validate_campaign = Mock()
        self._campagneManager._validate_campaign.return_value = campaign

        result = self._campagneManager.create_campaign(campaign)
        self.assertEquals(result, 1)
        record_campaigns_dao.add_or_update.assert_called_with(campaign)
        self._campagneManager._validate_campaign.assert_called_with(campaign)

    def test_get_campaigns_no_pagination(self):
        campaign = copy.deepcopy(self.sample_campaign)
        data = (1, [campaign])
        record_campaigns_dao.get_records = Mock()
        record_campaigns_dao.get_records.return_value = data

        (total, items) = self._campagneManager.get_campaigns()
        result = items[0]
        self.assertEqual(result.queue_name, self.queue_name)
        self.assertEqual(result.queue_display_name, self.queue_display_name)
        self.assertEqual(result.queue_number, self.queue_number)
        record_campaigns_dao.get_records.assert_called_with({}, False, (0, 0))

    def test_get_campaigns_paginated(self):
        campaign = copy.deepcopy(self.sample_campaign)
        data = (1, [campaign])
        record_campaigns_dao.get_records = Mock()
        record_campaigns_dao.get_records.return_value = data

        (total, items) = self._campagneManager.get_campaigns({"campaign_name": campaign.campaign_name},
                                                             True,
                                                             (1, 1))
        result = items[0]
        self.assertEqual(result.queue_name, self.queue_name)
        self.assertEqual(result.queue_display_name, self.queue_display_name)
        self.assertEqual(result.queue_number, self.queue_number)
        record_campaigns_dao.get_records.assert_called_with({"campaign_name": campaign.campaign_name},
                                                             True,
                                                             (1, 1))
    @patch('xivo_restapi.services.campagne_management.CampagneManagement._validate_campaign')
    def test_update_campaign(self, mock_validate):
        campaign_id = 1
        campaign_name = "campagne"
        queue_id = "1"
        base_filename = campaign_name + "-"
        campaign = copy.deepcopy(self.sample_campaign)
        data = {"campaign_name": campaign_name,
                "activated": False,
                "base_filename": base_filename,
                "queue_id": queue_id
                }
        record_campaigns_dao.get = Mock()
        record_campaigns_dao.get.return_value = campaign
        record_campaigns_dao.add_or_update = Mock()
        record_campaigns_dao.add_or_update.return_value = True

        result = self._campagneManager.update_campaign(campaign_id,
                                                              data)
        self.assertTrue(result)
        record_campaigns_dao.get.assert_called_once_with(campaign_id)
        record_campaigns_dao.add_or_update.assert_called_once_with(campaign)
        self.assertEqual(campaign.campaign_name, data['campaign_name'])
        self.assertEqual(campaign.activated, data['activated'])
        self.assertEqual(campaign.base_filename, data['base_filename'])
        self.assertEqual(campaign.queue_id, data['queue_id'])

    def test_delete_no_such_element(self):
        record_campaigns_dao.get = Mock()
        record_campaigns_dao.get.return_value = None
        self.assertRaises(NoSuchElementException, self._campagneManager.delete, '1')

    def test_delete_integrity_error(self):
        def mock_delete(campaign):
            raise IntegrityError(None, None, None)
        record_campaigns_dao.delete = Mock()
        record_campaigns_dao.delete.side_effect = mock_delete
        record_campaigns_dao.get = Mock()
        record_campaigns_dao.get.return_value = RecordCampaigns()
        self.assertRaises(IntegrityError, self._campagneManager.delete, '1')

    def test_delete_success(self):
        obj = RecordCampaigns()
        record_campaigns_dao.get = Mock()
        record_campaigns_dao.get.return_value = obj
        record_campaigns_dao.delete = Mock()
        record_campaigns_dao.delete.return_value = None
        self._campagneManager.delete('1')
        record_campaigns_dao.delete.assert_called_with(obj)

    def _create_sample_campaign(self):
        self.sample_campaign = RecordCampaigns()
        self.sample_campaign.activated = True
        self.sample_campaign.campaign_name = "campaign-àé"
        self.sample_campaign.queue_id = 1
        self.sample_campaign.base_filename = self.sample_campaign.campaign_name + "-"
        self.sample_campaign.start_date = datetime.strptime('2012-01-01 12:12:12',
                                                            "%Y-%m-%d %H:%M:%S")
        self.sample_campaign.end_date = datetime.strptime('2012-12-12 12:12:12',
                                                            "%Y-%m-%d %H:%M:%S")

    def test_validate_campaign(self):
        campaign = RecordCampaigns()
        campaign.campaign_name = None
        campaign.start_date = datetime.strptime('2012-12-31',
                                                "%Y-%m-%d")
        campaign.end_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        gotException = False
        try:
            self._campagneManager._validate_campaign(campaign)
        except InvalidInputException as e:
            self.assertTrue('empty_name' in e.errors_list)
            self.assertTrue('start_greater_than_end' in e.errors_list)
            gotException = True
        self.assertTrue(gotException)

        #we check that overlapping campaigns are rejected
        campaign1 = RecordCampaigns()
        campaign1.campaign_name = 'name1'
        campaign1.start_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        campaign1.end_date = datetime.strptime('2012-12-31',
                                                "%Y-%m-%d")
        campaign1.base_filename = 'file-'
        campaign1.activated = True
        campaign1.queue_id = 1
        campaign1.id = 1
        record_campaigns_dao.get_records = Mock()
        record_campaigns_dao.get_records.return_value = (1, [campaign1])
        campaign2 = copy.deepcopy(campaign1)
        campaign2.start_date = datetime.strptime('2012-02-28',
                                              "%Y-%m-%d")
        campaign2.end_date = datetime.strptime('2013-01-31',
                                                "%Y-%m-%d")
        campaign2.id = 2
        gotException = False
        try:
            self._campagneManager._validate_campaign(campaign2)
        except InvalidInputException as e:
            self.assertTrue('concurrent_campaigns' in e.errors_list)
            gotException = True
        self.assertTrue(gotException)
