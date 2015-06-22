# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from test_api import errors as e
from test_api import new_client


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
                              e.wrong_type(field='start_date', type='datetime'))

    def test_empty_end_date(self):
        response = self.client.call_logs.get(start_date='2013-01-29T00:00:00',
                                             end_date='')
        response.assert_match(400,
                              e.wrong_type(field='end_date', type='datetime'))
