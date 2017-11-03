# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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

from hamcrest import (assert_that,
                      has_entries,
                      has_item)

from test_api import fixtures
from test_api import scenarios as s
from . import confd

FAKE_ID = 999999999


def test_get_errors():
    fake_get = confd.cti_profiles(FAKE_ID).get
    yield s.check_resource_not_found, fake_get, 'CtiProfile'


@fixtures.cti_profile()
def test_list(cti_profile):
    response = confd.cti_profiles.get()
    assert_that(response.items, has_item(has_entries(id=cti_profile['id'],
                                                     name=cti_profile['name'])))


@fixtures.cti_profile()
def test_get(cti_profile):
    response = confd.cti_profiles(cti_profile['id']).get()
    assert_that(response.item, has_entries(id=cti_profile['id'],
                                           name=cti_profile['name']))
