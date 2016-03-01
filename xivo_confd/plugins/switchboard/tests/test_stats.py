# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from datetime import datetime
from hamcrest import assert_that
from hamcrest import contains
from hamcrest import has_entries
from unittest import TestCase

from ..stats import HourlyStatAccumulator


class StatMock(object):

    def __init__(self, time=datetime(2016, 3, 1, 0, 0, 0), end_type='abandoned', wait_time=1):
        self.time = time
        self.end_type = end_type
        self.wait_time = wait_time


class TestHourlyStatAccumulator(TestCase):

    def setUp(self):
        self.accumulator = HourlyStatAccumulator()

    def test_given_no_stats_then_no_results(self):
        assert_that(self.accumulator.results(), contains())

    def test_given_some_stats_then_results_have_dates_by_day(self):
        stats = [StatMock(time=datetime(2016, 3, 1, 11, 0, 0)),
                 StatMock(time=datetime(2016, 3, 1, 22, 0, 0)),
                 StatMock(time=datetime(2016, 3, 2, 00, 0, 0))]

        self.accumulator.accumulate(stats)

        assert_that(self.accumulator.results(), contains(has_entries(date='2016-03-01'),
                                                         has_entries(date='2016-03-02')))

    def test_abandoned(self):
        stats = [
            StatMock(end_type='abandoned'),    # +1
            StatMock(end_type='completed'),    # +0
            StatMock(end_type='forwarded'),    # +0
            StatMock(end_type='transferred'),  # +0
            StatMock(end_type='abandoned')     # +1
        ]

        self.accumulator.accumulate(stats)

        assert_that(self.accumulator.results(), contains(has_entries(abandoned=2)))

    def test_forwarded(self):
        stats = [
            StatMock(end_type='abandoned'),    # +0
            StatMock(end_type='completed'),    # +0
            StatMock(end_type='forwarded'),    # +1
            StatMock(end_type='transferred'),  # +0
            StatMock(end_type='forwarded')     # +1
        ]

        self.accumulator.accumulate(stats)

        assert_that(self.accumulator.results(), contains(has_entries(forwarded=2)))

    def test_transferred(self):
        stats = [
            StatMock(end_type='abandoned'),    # +0
            StatMock(end_type='completed'),    # +0
            StatMock(end_type='forwarded'),    # +0
            StatMock(end_type='transferred'),  # +1
            StatMock(end_type='transferred')   # +1
        ]

        self.accumulator.accumulate(stats)

        assert_that(self.accumulator.results(), contains(has_entries(transferred=2)))

    def test_answered(self):
        stats = [
            StatMock(end_type='abandoned'),    # +0
            StatMock(end_type='completed'),    # +1
            StatMock(end_type='forwarded'),    # +0
            StatMock(end_type='transferred'),  # +1
            StatMock(end_type='completed'),    # +1
            StatMock(end_type='transferred'),  # +1
        ]

        self.accumulator.accumulate(stats)

        assert_that(self.accumulator.results(), contains(has_entries(answered=4)))

    def test_entered(self):
        stats = [
            StatMock(end_type='abandoned'),    # +1
            StatMock(end_type='completed'),    # +1
            StatMock(end_type='forwarded'),    # +1
            StatMock(end_type='transferred'),  # +1
        ]

        self.accumulator.accumulate(stats)

        assert_that(self.accumulator.results(), contains(has_entries(entered=4)))

    def test_wait_time_average(self):
        stats = [
            StatMock(end_type='abandoned', wait_time=1),    # +1
            StatMock(end_type='completed', wait_time=2),    # +1
            StatMock(end_type='forwarded', wait_time=4),    # +1
            StatMock(end_type='transferred', wait_time=5),  # +1
        ]

        self.accumulator.accumulate(stats)

        assert_that(self.accumulator.results(), contains(has_entries(waiting_time_average=3)))
