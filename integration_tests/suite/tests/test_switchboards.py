# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from __future__ import unicode_literals

from datetime import datetime
from hamcrest import assert_that
from hamcrest import contains
from hamcrest import equal_to
from hamcrest import has_entries
from hamcrest import has_item

from test_api import confd
from test_api import fixtures
from test_api import scenarios as s

FAKE_ID = '12345'


@fixtures.switchboard()
@fixtures.switchboard()
def test_list_switchboards(first, second):
    response = confd.switchboards.get()

    assert_that(response.items, contains(has_entries(first), has_entries(second)))
    assert_that(response.total, equal_to(2))


def test_stats_switchboard_not_found():
    yield s.check_resource_not_found, confd.switchboards(FAKE_ID).stats.get, 'Switchboard'


@fixtures.switchboard_stat(time=datetime(2016, 3, 1, 11, 47, 23),
                           end_type='transferred',
                           wait_time=12)
def test_stats_switchboard(stat):
    expected = has_entries(date='2016-03-01',
                           entered='1',
                           answered='1',
                           transferred='1',
                           abandoned='0',
                           forwarded='0',
                           waiting_time_average='00:12')

    response = confd.switchboards(stat['queue_id']).stats.get()

    assert_that(response.csv(), has_item(expected))
