# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from . import confd

FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


@fixtures.group()
@fixtures.user()
def test_associate_errors(group, user):
    response = confd.users(FAKE_UUID).groups.put(groups=[group])
    response.assert_status(404)

    url = confd.users(user['uuid']).groups
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


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
        assert_that(
            response.item,
            has_entries(
                groups=contains_inanyorder(
                    has_entries(id=group1['id']),
                    has_entries(id=group2['id']),
                    has_entries(id=group3['id']),
                )
            ),
        )


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
    with a.user_line(user, line), a.group_member_user(
        group1, user
    ), a.group_member_user(group2, user):
        response = confd.users(user['uuid']).groups.put(groups=[])
        response.assert_updated()


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_dissociate_with_multi_line_user(group, user, line_1, line_2):
    with a.user_line(user, line_1), a.user_line(user, line_2, check=False):
        with a.group_member_user(group, user):
            # The group member is the interface of the main line of the user.
            # Deleting the any secondary line should keep the user in the group
            # Deleting the main line will remove the user from the group
            response = confd.lines(line_2['id']).delete()
            response.assert_deleted()

            response = confd.users(user['uuid']).get()
            assert_that(
                response.item,
                has_entries(
                    groups=contains_inanyorder(
                        has_entries(id=group['id']),
                    )
                ),
            )


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_bus_events(group, user, line):
    with a.user_line(user, line):
        url = confd.users(user['uuid']).groups.put
        body = {'groups': [group]}
        headers = {
            'tenant_uuid': user['tenant_uuid'],
            f'user_uuid:{user["uuid"]}': True,
        }

        s.check_event('user_groups_associated', headers, url, body)
