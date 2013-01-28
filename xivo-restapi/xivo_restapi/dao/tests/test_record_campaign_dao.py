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
from xivo_restapi.dao.exceptions import DataRetrieveError, \
    InvalidInputException
from xivo_restapi.dao.helpers.dynamic_formatting import \
    table_list_to_list_dict
from xivo_restapi.dao.record_campaign_dao import RecordCampaignDao, \
    RecordCampaignDbBinder
from xivo_restapi.dao.recording_details_dao import RecordingDetailsDao, \
    RecordingDetailsDbBinder
import copy
import unittest
from xivo_dao.helpers.db_manager import DbSession


class TestRecordCampaignDao(unittest.TestCase):
    '''
    Test pre-conditions:
    - a least one queue configured
    - a table called record_campaign in Asterisk database :

    CREATE TABLE record_campaign
    (
      campaign_name character varying(128) NOT NULL PRIMARY KEY,
      activated boolean NOT NULL,
      base_filename character varying(64) NOT NULL,
      queue_id integer NOT NULL REFERENCES queuefeatures(id)
          ON UPDATE NO ACTION ON DELETE NO ACTION
    )
    WITH (
      OIDS=FALSE
    );
    ALTER TABLE record_campaign
      OWNER TO asterisk;
    '''

    def setUp(self):
        self.record_db = RecordCampaignDbBinder()
        if self.record_db == None:
            self.fail("record_db is None, database connection error")
        self.recording_details_db = RecordingDetailsDbBinder()
        if self.recording_details_db == None:
            self.fail("record_db is None, database connection error")
        DbSession().query(RecordingDetailsDao).delete()
        DbSession().commit()
        DbSession().query(RecordCampaignDao).delete()
        DbSession().commit()
        unittest.TestCase.setUp(self)

    def test_get_records(self):
        campaign_name = "campaign-àé"
        queue_id = "1"
        base_filename = campaign_name + "-"

        expected_dict = {
            "campaign_name": campaign_name,
            "activated": "False",
            "base_filename": base_filename,
            "queue_id": queue_id,
            "start_date": '2012-01-01 12:12:12',
            "end_date": '2012-12-12 12:12:12',
        }

        obj = RecordCampaignDao()
        for k, v in expected_dict.items():
            setattr(obj, k, v)

        DbSession().add(obj)
        DbSession().commit()
        expected_dict['id'] = str(obj.id)
        records = self.record_db.get_records()['data']
        self.assertDictEqual(expected_dict, records[0])

    def test_id_from_name(self):
        campaign_name = "campaign-àé"
        queue_id = "1"
        base_filename = campaign_name + "-"

        expected_dict = {
            "campaign_name": campaign_name,
            "activated": "False",
            "base_filename": base_filename,
            "queue_id": queue_id,
            "start_date": '2012-01-01 12:12:12',
            "end_date": '2012-12-12 12:12:12',
        }

        obj = RecordCampaignDao()
        for k, v in expected_dict.items():
            setattr(obj, k, v)

        DbSession().add(obj)
        DbSession().commit()
        retrieved_id = self.record_db\
                .id_from_name(expected_dict['campaign_name'])
        self.assertTrue(retrieved_id == obj.id)

        with self.assertRaises(DataRetrieveError):
            self.record_db.id_from_name('test')

    def test_add(self):
        campaign_name = "campaign-àé"
        queue_id = "1"
        base_filename = campaign_name + "-"

        expected_dict = {
            "campaign_name": campaign_name,
            "activated": "False",
            "base_filename": base_filename,
            "queue_id": queue_id,
            "start_date": '2012-01-01 12:12:12',
            "end_date": '2012-12-12 12:12:12',
        }

        gen_id = self.record_db.add(expected_dict)

        expected_dict['id'] = str(gen_id)
        result = DbSession().query(RecordCampaignDao).all()
        self.assertTrue(len(result) == 1)
        result = table_list_to_list_dict(result)
        self.assertTrue(result[0] == expected_dict)

    def test_update(self):
        campaign_name = "campaign-àé"
        queue_id = "1"
        base_filename = campaign_name + "-"

        inserted_dict = {
            "campaign_name": campaign_name,
            "activated": "False",
            "base_filename": base_filename,
            "queue_id": queue_id,
            "start_date": '2012-01-01 12:12:12',
            "end_date": '2012-12-12 12:12:12',
        }

        obj = RecordCampaignDao()
        for k, v in inserted_dict.items():
            setattr(obj, k, v)

        DbSession().add(obj)
        DbSession().commit()
        queue_id2 = '2'

        updated_dict = {
            "campaign_name": campaign_name + str(1),
            "activated": "True",
            "base_filename": base_filename + str(1),
            "queue_id": queue_id2,
            "start_date": '2012-01-01 12:12:13',
            "end_date": '2012-12-12 12:12:13',
        }
        self.record_db.update(obj.id, updated_dict)
        updated_dict['id'] = str(obj.id)
        result = DbSession().query(RecordCampaignDao).all()
        self.assertTrue(len(result) == 1)
        result = table_list_to_list_dict(result)
        self.assertDictEqual(result[0], updated_dict)

    def test_validate_campaign(self):
        campaign = RecordCampaignDao()
        campaign.campaign_name = None
        campaign.start_date = datetime.strptime('2012-12-31',
                                                "%Y-%m-%d")
        campaign.end_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        gotException = False
        try:
            self.record_db._validate_campaign(campaign)
        except InvalidInputException as e:
            self.assertIn('empty_name', e.errors_list)
            self.assertIn('start_greater_than_end', e.errors_list)
            gotException = True
        self.assertTrue(gotException)

        #we check that overlapping campaigns are rejected
        campaign1 = RecordCampaignDao()
        campaign1.campaign_name = 'name1'
        campaign1.start_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        campaign1.end_date = datetime.strptime('2012-12-31',
                                                "%Y-%m-%d")
        campaign1.base_filename = 'file-'
        campaign1.activated = True
        campaign1.queue_id = 1
        campaign2 = copy.deepcopy(campaign1)
        DbSession().add(campaign1)
        DbSession().commit()
        campaign2.start_date = datetime.strptime('2012-02-28',
                                              "%Y-%m-%d")
        campaign2.end_date = datetime.strptime('2013-01-31',
                                                "%Y-%m-%d")
        gotException = False
        try:
            self.record_db._validate_campaign(campaign2)
        except InvalidInputException as e:
            self.assertIn('concurrent_campaigns', e.errors_list)
            gotException = True
        self.assertTrue(gotException)
