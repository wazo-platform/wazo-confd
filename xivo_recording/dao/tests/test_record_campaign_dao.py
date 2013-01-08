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

from xivo_dao.alchemy import dbconnection
from xivo_recording.dao.record_campaign_dao import RecordCampaignDao, \
    RecordCampaignDbBinder
from xivo_recording.recording_config import RecordingConfig
import random
import unittest


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

    def test_record_campaign_db(self):

        unique_id = str(random.randint(10000, 99999999))
        campaign_name = "campaign-àé" + unique_id
        queue_id = "1"
        base_filename = campaign_name + "-"

        expected_dict = {
            u"campaign_name": campaign_name,
            u"activated": "False",
            u"base_filename": base_filename,
            u"queue_id": queue_id,
            u"start_date": '2012-01-01 12:12:12',
            u"end_date": '2012-12-12 12:12:12',
        }

        expected_object = RecordCampaignDao()
        for k, v in expected_dict.items():
            setattr(expected_object, k, v)

        dbconnection.unregister_db_connection_pool()
        dbconnection.register_db_connection_pool(dbconnection.DBConnectionPool(dbconnection.DBConnection))
        dbconnection.add_connection(RecordingConfig.RECORDING_DB_URI)

        record_db = RecordCampaignDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
        if record_db == None:
            self.fail("record_db is None, database connexion error")

        expected_dict[u"id"] = str(record_db.add(expected_dict))

        records = record_db.get_records_as_dict()

        print("read from database:")
        for record in records:
            print(str(record))

        print("saved:")
        print(str(expected_dict))

        self.assert_(expected_dict in records)
