# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

from hamcrest import (assert_that,
                      contains_inanyorder,
                      has_entries)

from ..test_api import errors as e
from ..test_api import scenarios as s
from . import confd
from ..test_api import fixtures
from ..test_api import associations as a


FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


@fixtures.group()
@fixtures.user()
def test_associate_errors(group, user):
    response = confd.users(FAKE_UUID).groups.put(groups=[group])
    response.assert_status(404)

    url = confd.users(user['uuid']).groups.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'groups', 123
    yield s.check_bogus_field_returns_error, url, 'groups', None
    yield s.check_bogus_field_returns_error, url, 'groups', True
    yield s.check_bogus_field_returns_error, url, 'groups', 'string'
    yield s.check_bogus_field_returns_error, url, 'groups', [123]
    yield s.check_bogus_field_returns_error, url, 'groups', [None]
    yield s.check_bogus_field_returns_error, url, 'groups', ['string']
    yield s.check_bogus_field_returns_error, url, 'groups', [{}]
    yield s.check_bogus_field_returns_error, url, 'groups', [{'id': None}]
    yield s.check_bogus_field_returns_error, url, 'groups', [{'id': 1}, {'uuid': None}]
    yield s.check_bogus_field_returns_error, url, 'groups', [{'not_id': 123}]
    yield s.check_bogus_field_returns_error, url, 'groups', [{'id': FAKE_UUID}]


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_associate(group, user, line):
    with a.user_line(user, line):
        response = confd.users(user['uuid']).groups.put(groups=[group])
        response.assert_updated()


@fixtures.group()
@fixtures.group()
@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_associate_multiple(group1, group2, group3, user, line):
    with a.user_line(user, line):
        response = confd.users(user['uuid']).groups.put(groups=[group1, group2, group3])
        response.assert_updated()

        response = confd.users(user['uuid']).get()
        assert_that(response.item, has_entries(
            groups=contains_inanyorder(has_entries(id=group1['id']),
                                       has_entries(id=group2['id']),
                                       has_entries(id=group3['id']))
        ))


@fixtures.group()
@fixtures.user()
def test_associate_user_with_no_line(group, user):
    response = confd.users(user['uuid']).groups.put(groups=[group])
    response.assert_match(400, e.missing_association('User', 'Line'))


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_associate_same_group(group, user, line):
    with a.user_line(user, line):
        response = confd.users(user['uuid']).groups.put(group=[group, group])
        response.assert_status(400)


@fixtures.group()
@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_dissociate(group1, group2, user, line):
    with a.user_line(user, line), a.group_member_user(group1, user), a.group_member_user(group2, user):
        response = confd.users(user['uuid']).groups.put(groups=[])
        response.assert_updated()


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_bus_events(group, user, line):
    with a.user_line(user, line):
        url = confd.users(user['uuid']).groups.put
        body = {'groups': [group]}
        yield s.check_bus_event, 'config.users.groups.updated', url, body
