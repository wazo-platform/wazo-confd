# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (assert_that,
                      contains_inanyorder,
                      has_entries)

from ..helpers import errors as e
from ..helpers import scenarios as s
from . import confd
from ..helpers import fixtures
from ..helpers import associations as a


FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


def test_associate_errors():
    with fixtures.group() as group, fixtures.user() as user:
        response = confd.users(FAKE_UUID).groups.put(groups=[group])
        response.assert_status(404)

        url = confd.users(user['uuid']).groups.put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'groups', 123)
    s.check_bogus_field_returns_error(url, 'groups', None)
    s.check_bogus_field_returns_error(url, 'groups', True)
    s.check_bogus_field_returns_error(url, 'groups', 'string')
    s.check_bogus_field_returns_error(url, 'groups', [123])
    s.check_bogus_field_returns_error(url, 'groups', [None])
    s.check_bogus_field_returns_error(url, 'groups', ['string'])
    s.check_bogus_field_returns_error(url, 'groups', [{}])
    s.check_bogus_field_returns_error(url, 'groups', [{'id': None}])
    s.check_bogus_field_returns_error(url, 'groups', [{'id': 1}, {'uuid': None}])
    s.check_bogus_field_returns_error(url, 'groups', [{'not_id': 123}])
    s.check_bogus_field_returns_error(url, 'groups', [{'id': FAKE_UUID}])


def test_associate():
    with fixtures.group() as group, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            response = confd.users(user['uuid']).groups.put(groups=[group])
            response.assert_updated()


def test_associate_multiple():
    with fixtures.group() as group1, fixtures.group() as group2, fixtures.group() as group3, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            response = confd.users(user['uuid']).groups.put(groups=[group1, group2, group3])
            response.assert_updated()

            response = confd.users(user['uuid']).get()
            assert_that(response.item, has_entries(
                groups=contains_inanyorder(has_entries(id=group1['id']),
                                           has_entries(id=group2['id']),
                                           has_entries(id=group3['id']))
            ))


def test_associate_user_with_no_line():
    with fixtures.group() as group, fixtures.user() as user:
        response = confd.users(user['uuid']).groups.put(groups=[group])
        response.assert_match(400, e.missing_association('User', 'Line'))



def test_associate_same_group():
    with fixtures.group() as group, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            response = confd.users(user['uuid']).groups.put(group=[group, group])
            response.assert_status(400)


def test_dissociate():
    with fixtures.group() as group1, fixtures.group() as group2, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line), a.group_member_user(group1, user), a.group_member_user(group2, user):
            response = confd.users(user['uuid']).groups.put(groups=[])
            response.assert_updated()


def test_bus_events():
    with fixtures.group() as group, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            url = confd.users(user['uuid']).groups.put
            body = {'groups': [group]}
            s.check_bus_event('config.users.groups.updated', url, body)
