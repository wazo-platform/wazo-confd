# -*- coding: UTF-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
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

from datetime import datetime
from hamcrest import assert_that
from hamcrest import contains
from hamcrest import empty

from test_api import errors as e
from test_api import fixtures
from test_api.setup import new_client


class TestCallLogs(unittest.TestCase):

    def setUp(self):
        self.client = new_client({'Accept': 'text/csv'}).url

    def test_missing_start_date(self):
        response = self.client.call_logs.get(end_date='2013-01-29T00:00:00')
        response.assert_match(400,
                              e.missing_parameters('start_date'))

    def test_missing_end_date(self):
        response = self.client.call_logs.get(start_date='2013-01-29T00:00:00')
        response.assert_match(400,
                              e.missing_parameters('end_date'))

    def test_empty_start_date(self):
        response = self.client.call_logs.get(start_date='',
                                             end_date='2013-01-29T00:00:00')
        response.assert_match(400,
                              e.missing_parameters(field='start_date', type='datetime'))

    def test_empty_end_date(self):
        response = self.client.call_logs.get(start_date='2013-01-29T00:00:00',
                                             end_date='')
        response.assert_match(400,
                              e.missing_parameters(field='end_date', type='datetime'))

    @fixtures.call_log(date=datetime(2013, 1, 30, 8, 46, 20),
                       date_answer=datetime(2013, 1, 30, 8, 46, 20),
                       date_end=datetime(2013, 1, 30, 8, 46, 23),
                       source_name=u'Père Noël',
                       source_exten='1009',
                       destination_exten='1001')
    @fixtures.call_log(date=datetime(2013, 1, 30, 11, 3, 47),
                       date_answer=None,
                       date_end=datetime(2013, 1, 30, 11, 3, 47),
                       source_name='Bob Marley',
                       source_exten='1002',
                       destination_exten='4185550155')
    @fixtures.call_log(date=datetime(2013, 1, 30, 11, 20, 8),
                       date_answer=datetime(2013, 1, 30, 11, 20, 8),
                       date_end=datetime(2013, 1, 30, 11, 20, 11),
                       source_name='Bob Marley',
                       source_exten='1002',
                       destination_exten='4185550155',
                       user_field=u'Père Noël')
    def test_list_call_logs(self, _, __, ___):
        expected = contains({'Call Date': '2013-01-30T08:46:20',
                             'Caller': u'Père Noël (1009)',
                             'Called': '1001',
                             'Period': '3',
                             'user Field': ''},
                            {'Call Date': '2013-01-30T11:03:47',
                             'Caller': 'Bob Marley (1002)',
                             'Called': '4185550155',
                             'Period': '0',
                             'user Field': ''},
                            {'Call Date': '2013-01-30T11:20:08',
                             'Caller': 'Bob Marley (1002)',
                             'Called': '4185550155',
                             'Period': '3',
                             'user Field': u'Père Noël'})

        response = self.client.call_logs.get()

        assert_that(response.csv(), expected)

    @fixtures.call_log(date=datetime(2013, 1, 30, 8, 46, 20),
                       date_answer=datetime(2013, 1, 30, 8, 46, 20),
                       date_end=datetime(2013, 1, 30, 8, 46, 23),
                       source_name=u'Père, Noël',
                       source_exten='1009',
                       destination_exten='1001')
    def test_list_call_logs_with_csv_separator_inside_fields(self, _):
        expected = contains({'Call Date': '2013-01-30T08:46:20',
                             'Caller': u'Père, Noël (1009)',
                             'Called': '1001',
                             'Period': '3',
                             'user Field': ''})

        response = self.client.call_logs.get()

        assert_that(response.csv(), expected)

    @fixtures.call_log(date=datetime(2013, 1, 30, 8, 46, 20),
                       date_answer=datetime(2013, 1, 30, 8, 46, 20),
                       date_end=datetime(2013, 1, 30, 8, 46, 23),
                       source_name=u'Père, Noël',
                       source_exten='1009',
                       destination_exten='1001')
    def test_list_end_sooner_than_start(self, _):
        expected = empty()

        response = self.client.call_logs.get(start_date='2013-01-31T00:00:00',
                                             end_date='2013-01-30T00:00:00')

        assert_that(response.csv(), expected)

    @fixtures.call_log(date=datetime(2013, 1, 29, 8, 46, 20),
                       date_answer=datetime(2013, 1, 29, 8, 46, 20),
                       date_end=datetime(2013, 1, 29, 8, 46, 23),
                       source_name=u'Père Noël',
                       source_exten='1009',
                       destination_exten='1001')
    @fixtures.call_log(date=datetime(2013, 1, 30, 11, 13, 47),
                       date_answer=None,
                       date_end=datetime(2013, 1, 30, 11, 13, 48),
                       source_name='Bob Marley',
                       source_exten='1002',
                       destination_exten='4185550155')
    @fixtures.call_log(date=datetime(2013, 1, 31, 11, 20, 8),
                       date_answer=datetime(2013, 1, 31, 11, 20, 9),
                       date_end=datetime(2013, 1, 31, 11, 20, 12),
                       source_name='Bob Marley',
                       source_exten='1002',
                       destination_exten='4185550155',
                       user_field=u'Père Noël')
    def test_when_list_in_period_then_call_logs_are_filtered(self, _, __, ___):
        expected = contains({'Call Date': '2013-01-30T11:13:47',
                             'Caller': 'Bob Marley (1002)',
                             'Called': '4185550155',
                             'Period': '0',
                             'user Field': ''})

        response = self.client.call_logs.get(start_date='2013-01-30T11:11:11', end_date='2013-01-30T12:12:12')

        assert_that(response.csv(), expected)
