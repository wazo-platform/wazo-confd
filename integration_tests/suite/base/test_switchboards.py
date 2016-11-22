# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from test_api import confd
from test_api import errors as e
from test_api import fixtures
from test_api import scenarios as s

from hamcrest import (assert_that,
                      empty,
                      has_entries,
                      not_)


def test_get_errors():
    fake_switchboard = confd.switchboards(999999).get
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'


def test_delete_errors():
    fake_switchboard = confd.switchboards(999999).delete
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'


def test_post_errors():
    url = confd.switchboards.post
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}


def test_create_minimal_parameters():
    response = confd.switchboards.post(name='MySwitchboard')
    response.assert_created('switchboards')

    assert_that(response.item, has_entries(id=not_(empty()),
                                           name='MySwitchboard'))

    confd.switchboards(response.item['id']).delete().assert_deleted()


@fixtures.switchboard()
def test_delete(switchboard):
    response = confd.switchboards(switchboard['id']).delete()
    response.assert_deleted()
    response = confd.switchboards(switchboard['id']).get()
    response.assert_match(404, e.not_found(resource='Switchboard'))


@fixtures.switchboard()
def test_bus_events(switchboard):
    yield s.check_bus_event, 'config.switchboards.*.created', confd.switchboards.post, {'name': 'bus_event'}
    yield s.check_bus_event, 'config.switchboards.{id}.deleted'.format(id=switchboard['id']), confd.switchboards(switchboard['id']).delete
