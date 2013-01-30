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
from xivo_restapi.dao.record_campaign_dao import RecordCampaignDbBinder, \
    RecordCampaignDao
from xivo_restapi.dao.recording_details_dao import RecordingDetailsDao, \
    RecordingDetailsDbBinder
import copy
import unittest
from xivo_restapi.dao.helpers.dynamic_formatting import\
                    table_list_to_list_dict
from xivo_dao.helpers.db_manager import daosession_class


class TestRecordingDao(unittest.TestCase):
    '''
    Test pre-conditions:
    - a type called call_dir_type and a table called recording in Asterisk
    database :

    CREATE TYPE call_dir_type AS ENUM
      ('incoming',
      'outgoing');
    ALTER TYPE call_dir_type
      OWNER TO asterisk;

    CREATE TABLE recording
    (
      cid character varying(32) NOT NULL,
      call_direction call_dir_type,
      start_time timestamp without time zone,
      end_time timestamp without time zone,
      caller character varying(32),
      client_id character varying(1024),
      callee character varying(32),
      filename character varying(1024),
      campaign_id integer NOT NULL,
      agent_id integer NOT NULL,
      CONSTRAINT recording_pkey PRIMARY KEY (cid ),
      CONSTRAINT recording_agent_id_fkey FOREIGN KEY (agent_id)
          REFERENCES agentfeatures (id) MATCH SIMPLE
          ON UPDATE NO ACTION ON DELETE NO ACTION,
      CONSTRAINT recording_campaign_id_fkey FOREIGN KEY (campaign_id)
          REFERENCES record_campaign (id) MATCH SIMPLE
          ON UPDATE NO ACTION ON DELETE NO ACTION
    )
    WITH (
      OIDS=FALSE
    );
    ALTER TABLE recording
      OWNER TO asterisk;

    '''
    @daosession_class
    def setUp(self, session):
        self.record_db = RecordCampaignDbBinder()
        if self.record_db == None:
            self.fail("record_db is None, database connection error")
        self.recording_details_db = RecordingDetailsDbBinder()
        if self.recording_details_db == None:
            self.fail("record_db is None, database connection error")
        session.query(RecordingDetailsDao).delete()
        session.commit()
        self.campaign = RecordCampaignDao()
        self.campaign.campaign_name = 'name'
        self.campaign.base_filename = 'file-'
        self.campaign.queue_id = 1
        self.campaign.start_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        self.campaign.end_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        self.campaign.activated = True
        session.query(RecordCampaignDao).delete()
        session.add(self.campaign)
        session.commit()
        unittest.TestCase.setUp(self)

    @daosession_class
    def test_get_recordings_as_list(self, session):
        dict_data1 = {'cid': '001',
                     'caller': '2002',
                     'agent_id': '1',
                     'filename': 'file.wav',
                     'start_time': '2012-01-01 00:00:00',
                     'end_time': '2012-01-01 00:10:00',
                     'campaign_id': str(self.campaign.id)}
        dict_data2 = copy.deepcopy(dict_data1)
        dict_data2['cid'] = '002'
        dict_data2['caller'] = '3003'
        my_recording1 = RecordingDetailsDao()
        my_recording2 = RecordingDetailsDao()
        for k, v in dict_data1.items():
            setattr(my_recording1, k, v)
        for k, v in dict_data2.items():
            setattr(my_recording2, k, v)
        session.add(my_recording1)
        session.add(my_recording2)
        session.commit()

        search = {'caller': '2002'}
        result = self.recording_details_db\
                     .get_recordings_as_list(self.campaign.id, search)
        self.assertTrue(result['total'] == 1)
        self.assertDictContainsSubset(dict_data1, result['data'][0])

    @daosession_class
    def test_add_recording(self, session):
        dict_data1 = {'cid': '001',
                     'caller': '2002',
                     'agent_id': '1',
                     'filename': 'file.wav',
                     'start_time': '2012-01-01 00:00:00',
                     'end_time': '2012-01-01 00:10:00',
                     'campaign_id': str(self.campaign.id)}
        self.recording_details_db.add_recording(dict_data1)
        result = session.query(RecordingDetailsDao).all()
        result = table_list_to_list_dict(result)
        self.assertTrue(len(result) == 1)
        self.assertDictContainsSubset(dict_data1, result[0])

    @daosession_class
    def test_search_recordings(self, session):
        dict_data1 = {'cid': '001',
                     'caller': '2002',
                     'agent_id': '1',
                     'filename': 'file.wav',
                     'start_time': '2012-01-01 00:00:00',
                     'end_time': '2012-01-01 00:10:00',
                     'campaign_id': str(self.campaign.id)}
        dict_data2 = copy.deepcopy(dict_data1)
        dict_data2['cid'] = '002'
        dict_data2['caller'] = '3003'
        my_recording1 = RecordingDetailsDao()
        my_recording2 = RecordingDetailsDao()
        for k, v in dict_data1.items():
            setattr(my_recording1, k, v)
        for k, v in dict_data2.items():
            setattr(my_recording2, k, v)
        session.add(my_recording1)
        session.add(my_recording2)
        session.commit()

        key = '3003'
        result = self.recording_details_db\
                     .search_recordings(self.campaign.id, key)
        self.assertTrue(result['total'] == 1)
        self.assertDictContainsSubset(dict_data2, result['data'][0])

        key = '1000'
        result = self.recording_details_db\
                     .search_recordings(self.campaign.id, key)
        self.assertTrue(result['total'] == 2)
        self.assertDictContainsSubset(dict_data1, result['data'][0])
        self.assertDictContainsSubset(dict_data2, result['data'][1])

    @daosession_class
    def test_delete(self, session):
        result = self.recording_details_db.delete(1, '001')
        assert result == None
        dict_data1 = {'cid': '001',
                     'caller': '2002',
                     'agent_id': '1',
                     'filename': 'file.wav',
                     'start_time': '2012-01-01 00:00:00',
                     'end_time': '2012-01-01 00:10:00',
                     'campaign_id': str(self.campaign.id)}
        my_recording1 = RecordingDetailsDao()
        for k, v in dict_data1.items():
            setattr(my_recording1, k, v)
        session.add(my_recording1)
        session.commit()
        data = session.query(RecordingDetailsDao).all()
        self.assertTrue(len(data) == 1)
        data = table_list_to_list_dict(data)
        self.assertDictContainsSubset(dict_data1, data[0])
        result = self.recording_details_db.delete(self.campaign.id,
                                                  my_recording1.cid)
        data = session.query(RecordingDetailsDao)\
                                                                    .all()
        self.assertTrue(len(data) == 0)
        self.assertTrue(result == my_recording1.filename)
