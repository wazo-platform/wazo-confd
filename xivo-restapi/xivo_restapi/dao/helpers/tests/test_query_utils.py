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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from datetime import datetime
from sqlalchemy.sql.expression import asc
from xivo_dao.alchemy import dbconnection
from xivo_dao.helpers.db_manager import DbSession
from xivo_restapi.dao.exceptions import EmptyPageException, \
    InvalidPaginatorException
from xivo_restapi.dao.helpers import query_utils
from xivo_restapi.dao.record_campaign_dao import RecordCampaignDbBinder, \
    RecordCampaignDao
from xivo_restapi.dao.recording_details_dao import RecordingDetailsDao, \
    RecordingDetailsDbBinder
from xivo_restapi.restapi_config import RestAPIConfig
import random
import unittest


class TestQueryUtils(unittest.TestCase):

    def setUp(self):
        dbconnection.unregister_db_connection_pool()
        dbconnection.register_db_connection_pool(dbconnection\
                                .DBConnectionPool(dbconnection.DBConnection))
        dbconnection.add_connection(RestAPIConfig.RECORDING_DB_URI)
        self.record_db = RecordCampaignDbBinder()
        if self.record_db == None:
            self.fail("record_db is None, database connection error")
        self.recording_details_db = RecordingDetailsDbBinder()
        if self.recording_details_db == None:
            self.fail("recording_details_db is None, database connection error")
        DbSession().query(RecordingDetailsDao).delete()
        DbSession().commit()
        self.campaign = RecordCampaignDao()
        self.campaign.campaign_name = 'name'
        self.campaign.base_filename = 'file-'
        self.campaign.queue_id = 1
        self.campaign.start_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        self.campaign.end_date = datetime.strptime('2012-01-31',
                                              "%Y-%m-%d")
        self.campaign.activated = True
        DbSession().query(RecordCampaignDao).delete()
        DbSession().add(self.campaign)
        DbSession().commit()
        unittest.TestCase.setUp(self)

    def test_get_all_data(self):

        cid1 = '001'
        cid2 = '002'
        call_direction = "incoming"
        start_time = "2004-10-19 10:23:54"
        end_time = "2004-10-19 10:23:56"
        caller = "+" + str(random.randint(1000, 9999))
        agent_id = 1

        expected_dir1 = {"cid": cid1,
                        "campaign_id": self.campaign.id,
                        "call_direction": call_direction,
                        "start_time": start_time,
                        "end_time": end_time,
                        "caller": caller,
                        "agent_id": agent_id
                        }

        expected_object1 = RecordingDetailsDao()
        for k, v in expected_dir1.items():
            setattr(expected_object1, k, v)

        expected_dir2 = {"cid": cid2,
                        "campaign_id": self.campaign.id,
                        "call_direction": call_direction,
                        "start_time": start_time,
                        "end_time": end_time,
                        "caller": caller,
                        "agent_id": agent_id
                        }

        expected_object2 = RecordingDetailsDao()
        for k, v in expected_dir2.items():
            setattr(expected_object2, k, v)

        DbSession().add(expected_object1)
        DbSession().add(expected_object2)
        DbSession().commit()

        expected_list = [expected_object1, expected_object2].sort()
        result = query_utils.get_all_data(DbSession(),
                                          DbSession()\
                                          .query(RecordingDetailsDao))['data']\
                                          .sort()

        self.assertTrue(expected_list == result, "Expected: " + \
                             str(expected_list) + ", actual: " + str(result))

    def test_get_paginated_data(self):
        cid1 = "001"
        cid2 = "002"
        call_direction = "incoming"
        start_time = "2004-10-19 10:23:54"
        end_time = "2004-10-19 10:23:56"
        caller = "2002"
        agent_id = '1'

        expected_dir1 = {"cid": cid1,
                        "campaign_id": str(self.campaign.id),
                        "call_direction": call_direction,
                        "start_time": start_time,
                        "end_time": end_time,
                        "caller": caller,
                        "agent_id": agent_id,
                        'filename': '',
                        'client_id': '',
                        'callee': ''
                        }

        expected_object1 = RecordingDetailsDao()
        for k, v in expected_dir1.items():
            setattr(expected_object1, k, v)

        expected_dir2 = {"cid": cid2,
                        "campaign_id": str(self.campaign.id),
                        "call_direction": call_direction,
                        "start_time": start_time,
                        "end_time": end_time,
                        "caller": caller,
                        "agent_id": agent_id,
                        'filename': '',
                        'client_id': '',
                        'callee': ''
                        }

        expected_object2 = RecordingDetailsDao()
        for k, v in expected_dir2.items():
            setattr(expected_object2, k, v)

        DbSession().add(expected_object1)
        DbSession().add(expected_object2)
        DbSession().commit()

        list_paginators = [(1, 1), (2, 1), (1, 0), (0, 0), (999, 999), ('')]
        list_expected_results = [[expected_dir1], [expected_dir2]]
        list_expected_results.sort(key=(lambda x: x[0]['cid']))
        list_expected_results.append([])
        list_expected_results.append([])
        list_expected_results.append([])
        list_expected_results.append([])

        i = 0
        for paginator in list_paginators:
            expected_list = list_expected_results[i]
            if(i == 3):
                with self.assertRaises(InvalidPaginatorException):
                    result = query_utils.get_paginated_data(
                                        DbSession(),
                                        DbSession()\
                                          .query(RecordingDetailsDao)\
                                          .order_by(asc("cid")),
                                        paginator)['data']
            elif(i == 4):
                with self.assertRaises(EmptyPageException):
                    result = query_utils.get_paginated_data(
                                        DbSession(),
                                        DbSession()\
                                          .query(RecordingDetailsDao)\
                                          .order_by(asc("cid")),
                                        paginator)['data']
            elif(i == 5):
                with self.assertRaises(InvalidPaginatorException):
                    result = query_utils.get_paginated_data(
                                        DbSession(),
                                        DbSession()\
                                          .query(RecordingDetailsDao)\
                                          .order_by(asc("cid")),
                                        paginator)['data']
            else:
                result = query_utils.get_paginated_data(
                                        DbSession(),
                                        DbSession()\
                                          .query(RecordingDetailsDao)\
                                          .order_by(asc("cid")),
                                        paginator)['data']
                self.assertListEqual(expected_list, result)
            i += 1

        DbSession().query(RecordingDetailsDao).delete()
        DbSession().commit()
