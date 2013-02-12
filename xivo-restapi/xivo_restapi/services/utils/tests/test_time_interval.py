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
from xivo_restapi.services.utils.time_interval import TimeInterval
import unittest


class Test(unittest.TestCase):

    def test_init(self):
        self.assertRaises(Exception, TimeInterval, '', '')
        self.assertRaises(Exception, TimeInterval,
                          datetime.strptime("2012-12-31", "%Y-%m-%d"),
                          datetime.strptime("2012-01-01", "%Y-%m-%d"))

    def test_intersect(self):
        interval1 = TimeInterval(datetime.strptime("2012-01-01", "%Y-%m-%d"),
                                 datetime.strptime("2012-03-01", "%Y-%m-%d"))
        interval2 = TimeInterval(datetime.strptime("2012-02-01", "%Y-%m-%d"),
                                 datetime.strptime("2012-03-31", "%Y-%m-%d"))
        result = interval2.intersect(interval1)
        self.assertTrue(result._start_date == datetime.strptime("2012-02-01",
                                                                "%Y-%m-%d"))
        self.assertTrue(result._end_date == datetime.strptime("2012-03-01",
                                                              "%Y-%m-%d"))

        interval1 = TimeInterval(datetime.strptime("2012-01-01", "%Y-%m-%d"),
                                 datetime.strptime("2012-02-01", "%Y-%m-%d"))
        interval2 = TimeInterval(datetime.strptime("2012-03-01", "%Y-%m-%d"),
                                 datetime.strptime("2012-03-31", "%Y-%m-%d"))
        result = interval2.intersect(interval1)
        self.assertTrue(result == None)
