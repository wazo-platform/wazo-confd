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

import unittest
import random
from dao.record_campaign_dao import RecordCampaignDao, RecordCampaignDbBinder
from xivo_dao.alchemy import dbconnection
from recording_config import RecordingConfig
from dao.tests.table_utils import contains


class TestRecordCampaignDao(unittest.TestCase):
    '''
    Test pre-conditions:
    - an queue named "prijem"
    - a table called record_campaign in Asterisk database :

   CREATE TABLE record_campaign
    (
      uniqueid character varying(32) NOT NULL,
      base_filename character varying(64) NOT NULL,
      queue_name character varying(255) NOT NULL,
      CONSTRAINT record_campaign_pkey PRIMARY KEY (uniqueid ),
      CONSTRAINT record_campaign_fkey FOREIGN KEY (queue_name)
          REFERENCES queuefeatures (name) MATCH SIMPLE
          ON UPDATE NO ACTION ON DELETE NO ACTION
    )
    WITH (
      OIDS=FALSE
    );
    ALTER TABLE record_campaign
      OWNER TO asterisk;

    '''

    def test_record_campaign_db(self):

        uniqueid = str(random.randint(10000, 99999999))
        queue_name = "prijem"
        base_filename = queue_name + "-" + uniqueid + "-"

        expected_dir = {
            "uniqueid": uniqueid,
            "base_filename": base_filename,
            "queue_name": queue_name
        }

        expected_object = RecordCampaignDao()
        for k, v in expected_dir.items():
            setattr(expected_object, k, v)

        dbconnection.unregister_db_connection_pool()
        dbconnection.register_db_connection_pool(dbconnection.DBConnectionPool(dbconnection.DBConnection))
        dbconnection.add_connection(RecordingConfig.RECORDING_DB_URI)

        record_db = RecordCampaignDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
        record_db.insert_into(expected_dir)
        records = record_db.get_records()

        print("read from database:")
        for record in records:
            print(record.to_string())

        print("saved:")
        print(expected_object.to_string())

        self.assert_(contains(records, lambda record: record.to_string() == expected_object.to_string()), "Write/read from database failed")
