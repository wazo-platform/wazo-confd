# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    has_entries,
    has_items,
)

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


@fixtures.group()
@fixtures.user()
def test_associate_errors(group, user):
    response = confd.groups(FAKE_ID).members.users.put(users=[user])
    response.assert_status(404)

    url = confd.groups(group['id']).members.users.put
    error_checks(url)

    url = confd.groups(group['uuid']).members.users.put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'users', 123)
    s.check_bogus_field_returns_error(url, 'users', None)
    s.check_bogus_field_returns_error(url, 'users', True)
    s.check_bogus_field_returns_error(url, 'users', 'string')
    s.check_bogus_field_returns_error(url, 'users', [123])
    s.check_bogus_field_returns_error(url, 'users', [None])
    s.check_bogus_field_returns_error(url, 'users', ['string'])
    s.check_bogus_field_returns_error(url, 'users', [{}])
    s.check_bogus_field_returns_error(url, 'users', [{'uuid': None}])
    s.check_bogus_field_returns_error(url, 'users', [{'uuid': 1}, {'uuid': None}])
    s.check_bogus_field_returns_error(url, 'users', [{'not_uuid': 123}])
    s.check_bogus_field_returns_error(url, 'users', [{'uuid': FAKE_UUID}])

    regex = r'users.*priority'
    s.check_bogus_field_returns_error_matching_regex(
        url, 'users', [{'priority': None}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'users', [{'priority': 'string'}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'users', [{'priority': -1}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'users', [{'priority': []}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'users', [{'priority': {}}], regex
    )


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_associate(group, user, line):
    with a.user_line(user, line):
        response = confd.groups(group['id']).members.users.put(users=[user])
        response.assert_updated()

    with a.user_line(user, line):
        response = confd.groups(group['uuid']).members.users.put(users=[user])
        response.assert_updated()


@fixtures.group()
@fixtures.user()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multiple_with_priority(
    group, user1, user2, user3, line1, line2, line3
):
    with a.user_line(user1, line1), a.user_line(user2, line2), a.user_line(
        user3, line3
    ):
        user1['priority'], user2['priority'], user3['priority'] = 4, 1, 2
        response = confd.groups(group['uuid']).members.users.put(
            users=[user1, user2, user3]
        )
        response.assert_updated()

        response = confd.groups(group['uuid']).get()
        assert_that(
            response.item,
            has_entries(
                members=has_entries(
                    users=contains(
                        has_entries(uuid=user2['uuid'], priority=1),
                        has_entries(uuid=user3['uuid'], priority=2),
                        has_entries(uuid=user1['uuid'], priority=4),
                    )
                )
            ),
        )


@fixtures.group()
@fixtures.user()
def test_associate_user_with_no_line(group, user):
    response = confd.groups(group['uuid']).members.users.put(users=[user])
    response.assert_match(400, e.missing_association('User', 'Line'))


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_same_user(group, user, line1, line2):
    with a.user_line(user, line1), a.user_line(user, line2):
        response = confd.groups(group['uuid']).members.users.put(users=[user, user])
        response.assert_status(400)


@fixtures.group()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
def test_associate_multiple_user_with_same_line(group, user1, user2, line):
    with a.user_line(user1, line), a.user_line(user2, line):
        response = confd.groups(group['uuid']).members.users.put(users=[user1, user2])
        response.assert_match(
            400, re.compile('Cannot associate different users with the same line')
        )


@fixtures.group()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_get_users_associated_to_group(group, user1, user2, line1, line2):
    with a.user_line(user1, line1), a.user_line(user2, line2), a.group_member_user(
        group, user2, user1
    ):
        response = confd.groups(group['uuid']).get()
        assert_that(
            response.item,
            has_entries(
                members=has_entries(
                    users=contains_inanyorder(
                        has_entries(
                            uuid=user2['uuid'],
                            firstname=user2['firstname'],
                            lastname=user2['lastname'],
                        ),
                        has_entries(
                            uuid=user1['uuid'],
                            firstname=user1['firstname'],
                            lastname=user1['lastname'],
                        ),
                    )
                )
            ),
        )


@fixtures.group()
@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_get_groups_associated_to_user(group1, group2, user, line):
    with a.user_line(user, line), a.group_member_user(
        group2, user
    ), a.group_member_user(group1, user):
        response = confd.users(user['uuid']).get()
        assert_that(
            response.item,
            has_entries(
                groups=contains_inanyorder(
                    has_entries(
                        id=group2['id'],
                        uuid=group2['uuid'],
                        name=group2['name'],
                    ),
                    has_entries(
                        id=group1['id'],
                        uuid=group1['uuid'],
                        name=group1['name'],
                    ),
                )
            ),
        )

        response = confd.users.get()
        assert_that(
            response.items,
            has_items(
                has_entries(
                    uuid=user['uuid'],
                    groups=contains_inanyorder(
                        has_entries(id=group2['id'], uuid=group2['uuid']),
                        has_entries(id=group1['id'], uuid=group1['uuid']),
                    ),
                ),
            ),
        )


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_group, sub_group, main_user, sub_user):
    response = confd.groups(main_group['uuid']).members.users.put(
        users=[{'uuid': main_user['uuid']}], wazo_tenant=SUB_TENANT
    )
    response.assert_match(404, e.not_found('Group'))

    response = confd.groups(sub_group['uuid']).members.users.put(
        users=[{'uuid': main_user['uuid']}], wazo_tenant=SUB_TENANT
    )
    response.assert_match(400, e.not_found('User'))

    response = confd.groups(main_group['uuid']).members.users.put(
        users=[{'uuid': sub_user['uuid']}], wazo_tenant=MAIN_TENANT
    )
    response.assert_match(400, e.different_tenant())


@fixtures.group()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_dissociate(group, user1, user2, line1, line2):
    with a.user_line(user1, line1), a.user_line(user2, line2), a.group_member_user(
        group, user1, user2
    ):
        response = confd.groups(group['uuid']).members.users.put(users=[])
        response.assert_updated()

    with a.user_line(user1, line1), a.user_line(user2, line2), a.group_member_user(
        group, user1, user2
    ):
        response = confd.groups(group['id']).members.users.put(users=[])
        response.assert_updated()


@fixtures.group()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_delete_group_when_group_and_user_associated(group, user1, user2, line1, line2):
    with a.user_line(user1, line1), a.user_line(user2, line2), a.group_member_user(
        group, user1, user2, check=False
    ):
        confd.groups(group['uuid']).delete().assert_deleted()

        deleted_group = confd.groups(group['uuid']).get
        s.check_resource_not_found(deleted_group, 'Group')

        response = confd.users(user1['uuid']).get()
        assert_that(response.item['groups'], empty())

        response = confd.users(user2['uuid']).get()
        assert_that(response.item['groups'], empty())


@fixtures.group()
@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_delete_user_when_group_and_user_associated(group1, group2, user, line):
    with a.user_line(user, line, check=False), a.group_member_user(
        group1, user, check=False
    ), a.group_member_user(group2, user, check=False):
        confd.lines(line['id']).delete().assert_deleted()
        confd.users(user['uuid']).delete().assert_deleted()

        deleted_user = confd.users(user['uuid']).get
        s.check_resource_not_found(deleted_user, 'User')

        response = confd.groups(group1['uuid']).get()
        assert_that(response.item['members']['users'], empty())

        response = confd.groups(group2['uuid']).get()
        assert_that(response.item['members']['users'], empty())


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_bus_events(group, user, line):
    with a.user_line(user, line):
        url = confd.groups(group['uuid']).members.users.put
        body = {'users': [user]}
        headers = {'tenant_uuid': MAIN_TENANT}

        s.check_event('group_member_users_associated', headers, url, body)
