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

from sqlalchemy.sql.expression import asc
from xivo_dao.alchemy import dbconnection
from xivo_recording.dao.helpers import query_utils
from xivo_recording.dao.recording_details_dao import RecordingDetailsDao, \
    RecordingDetailsDbBinder
from xivo_recording.recording_config import RecordingConfig
import random
import unittest
from xivo_recording.dao.exceptions import EmptyPageException,\
    InvalidPaginatorException


class TestQueryUtils(unittest.TestCase):

    def setUp(self):
        RecordingConfig.RECORDING_DB_URI = "postgresql://asterisk:proformatique@127.0.0.1:5433/asterisk"
        dbconnection.unregister_db_connection_pool()
        dbconnection.register_db_connection_pool(dbconnection.DBConnectionPool(dbconnection.DBConnection))
        dbconnection.add_connection(RecordingConfig.RECORDING_DB_URI)
        unittest.TestCase.setUp(self)

    def test_get_all_data(self):

        record_db = RecordingDetailsDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
        record_db.session.query(RecordingDetailsDao).delete()

        cid1 = str(random.randint(10000, 99999999))
        cid2 = str(random.randint(10000, 99999999))
        call_direction = "incoming"
        start_time = "2004-10-19 10:23:54"
        end_time = "2004-10-19 10:23:56"
        caller = "+" + str(random.randint(1000, 9999))
        campaign_id = 1
        agent_id = 50

        expected_dir1 = {"cid": cid1,
                        "campaign_id": campaign_id,
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
                        "campaign_id": campaign_id,
                        "call_direction": call_direction,
                        "start_time": start_time,
                        "end_time": end_time,
                        "caller": caller,
                        "agent_id": agent_id
                        }

        expected_object2 = RecordingDetailsDao()
        for k, v in expected_dir2.items():
            setattr(expected_object2, k, v)

        record_db.session.add(expected_object1)
        record_db.session.add(expected_object2)
        record_db.session.commit()

        expected_list = [expected_object1, expected_object2].sort()
        result = query_utils.get_all_data(record_db.session,
                                          record_db.session.query(RecordingDetailsDao))['data'].sort()

        record_db.session.query(RecordingDetailsDao).delete()
        record_db.session.commit()

        assert expected_list == result, "Expected: " + str(expected_list) + "actual: " + str(result)

    def test_get_paginated_data(self):
        record_db = RecordingDetailsDbBinder.new_from_uri(RecordingConfig.RECORDING_DB_URI)
        record_db.session.query(RecordingDetailsDao).delete()

        cid1 = unicode(str(random.randint(10000, 99999999)), "utf-8")
        cid2 = unicode(str(random.randint(10000, 99999999)), "utf-8")
        call_direction = u"incoming"
        start_time = "2004-10-19 10:23:54"
        end_time = "2004-10-19 10:23:56"
        caller = u"+" + str(random.randint(1000, 9999))
        campaign_id = "1"
        agent_id = "50"

        expected_dir1 = {u"cid": cid1,
                        u"campaign_id": campaign_id,
                        u"call_direction": call_direction,
                        u"start_time": start_time,
                        u"end_time": end_time,
                        u"caller": caller,
                        u"agent_id": agent_id,
                        u'filename': '',
                        u'client_id': '',
                        u'callee': ''
                        }

        expected_object1 = RecordingDetailsDao()
        for k, v in expected_dir1.items():
            setattr(expected_object1, k, v)

        expected_dir2 = {u"cid": cid2,
                        u"campaign_id": campaign_id,
                        u"call_direction": call_direction,
                        u"start_time": start_time,
                        u"end_time": end_time,
                        u"caller": caller,
                        u"agent_id": agent_id,
                        u'filename': '',
                        u'client_id': '',
                        u'callee': ''
                        }

        expected_object2 = RecordingDetailsDao()
        for k, v in expected_dir2.items():
            setattr(expected_object2, k, v)

        record_db.session.add(expected_object1)
        record_db.session.add(expected_object2)
        record_db.session.commit()

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
                    result = query_utils.get_paginated_data(record_db.session,
                                          record_db.session.query(RecordingDetailsDao)\
                                          .order_by(asc("cid")), paginator)['data']
            elif(i == 4):
                with self.assertRaises(EmptyPageException):
                    result = query_utils.get_paginated_data(record_db.session,
                                          record_db.session.query(RecordingDetailsDao)\
                                          .order_by(asc("cid")), paginator)['data']
            elif(i==5):
                with self.assertRaises(InvalidPaginatorException):
                    result = query_utils.get_paginated_data(record_db.session,
                                          record_db.session.query(RecordingDetailsDao)\
                                          .order_by(asc("cid")), paginator)['data']
            else:
                result = query_utils.get_paginated_data(record_db.session,
                                          record_db.session.query(RecordingDetailsDao)\
                                          .order_by(asc("cid")), paginator)['data']
                self.assert_(expected_list == result, "Unexpected result: " + \
                             str(result) + ",\n expected was: " + str(expected_list))

            i += 1

        record_db.session.query(RecordingDetailsDao).delete()
        record_db.session.commit()
