# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    has_entries,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


@fixtures.group()
@fixtures.user()
def test_associate_errors(group, user):
    response = confd.groups(FAKE_ID).members.users.put(users=[user])
    response.assert_status(404)

    url = confd.groups(group['id']).members.users.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'users', 123
    yield s.check_bogus_field_returns_error, url, 'users', None
    yield s.check_bogus_field_returns_error, url, 'users', True
    yield s.check_bogus_field_returns_error, url, 'users', 'string'
    yield s.check_bogus_field_returns_error, url, 'users', [123]
    yield s.check_bogus_field_returns_error, url, 'users', [None]
    yield s.check_bogus_field_returns_error, url, 'users', ['string']
    yield s.check_bogus_field_returns_error, url, 'users', [{}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'uuid': None}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'uuid': 1}, {'uuid': None}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'not_uuid': 123}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'uuid': FAKE_UUID}]

    regex = r'users.*priority'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'users', [{'priority': None}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'users', [{'priority': 'string'}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'users', [{'priority': -1}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'users', [{'priority': []}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'users', [{'priority': {}}], regex


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_associate(group, user, line):
    with a.user_line(user, line):
        response = confd.groups(group['id']).members.users.put(users=[user])
        response.assert_updated()


@fixtures.group()
@fixtures.user()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multiple_with_priority(group, user1, user2, user3, line1, line2, line3):
    with a.user_line(user1, line1), a.user_line(user2, line2), a.user_line(user3, line3):
        user1['priority'], user2['priority'], user3['priority'] = 4, 1, 2
        response = confd.groups(group['id']).members.users.put(users=[user1, user2, user3])
        response.assert_updated()

        response = confd.groups(group['id']).get()
        assert_that(response.item, has_entries(
            members=has_entries(users=contains(
                has_entries(uuid=user2['uuid'], priority=1),
                has_entries(uuid=user3['uuid'], priority=2),
                has_entries(uuid=user1['uuid'], priority=4),
            ))
        ))


@fixtures.group()
@fixtures.user()
def test_associate_user_with_no_line(group, user):
    response = confd.groups(group['id']).members.users.put(users=[user])
    response.assert_match(400, e.missing_association('User', 'Line'))


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_same_user(group, user, line1, line2):
    with a.user_line(user, line1), a.user_line(user, line2):
        response = confd.groups(group['id']).members.users.put(users=[user, user])
        response.assert_status(400)


@fixtures.group()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
def test_associate_multiple_user_with_same_line(group, user1, user2, line):
    with a.user_line(user1, line), a.user_line(user2, line):
        response = confd.groups(group['id']).members.users.put(users=[user1, user2])
        response.assert_match(400, re.compile('Cannot associate different users with the same line'))


@fixtures.group()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_get_users_associated_to_group(group, user1, user2, line1, line2):
    with a.user_line(user1, line1), a.user_line(user2, line2), \
            a.group_member_user(group, user2, user1):
        response = confd.groups(group['id']).get()
        assert_that(response.item, has_entries(
            members=has_entries(users=contains_inanyorder(
                has_entries(uuid=user2['uuid'], firstname=user2['firstname'], lastname=user2['lastname']),
                has_entries(uuid=user1['uuid'], firstname=user1['firstname'], lastname=user1['lastname']),
            ))
        ))


@fixtures.group()
@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_get_groups_associated_to_user(group1, group2, user, line):
    with a.user_line(user, line), a.group_member_user(group2, user), a.group_member_user(group1, user):
        response = confd.users(user['uuid']).get()
        assert_that(response.item, has_entries(
            groups=contains_inanyorder(
                has_entries(id=group2['id'], name=group2['name']),
                has_entries(id=group1['id'], name=group1['name']),
            )
        ))


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_group, sub_group, main_user, sub_user):
    response = confd.groups(main_group['id']).members.users.put(
        users=[{'uuid': main_user['uuid']}],
        wazo_tenant=SUB_TENANT,
    )
    response.assert_match(404, e.not_found('Group'))

    response = confd.groups(sub_group['id']).members.users.put(
        users=[{'uuid': main_user['uuid']}],
        wazo_tenant=SUB_TENANT,
    )
    response.assert_match(400, e.not_found('User'))

    response = confd.groups(main_group['id']).members.users.put(
        users=[{'uuid': sub_user['uuid']}],
        wazo_tenant=MAIN_TENANT,
    )
    response.assert_match(400, e.different_tenant())


@fixtures.group()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_dissociate(group, user1, user2, line1, line2):
    with a.user_line(user1, line1), a.user_line(user2, line2), a.group_member_user(group, user1, user2):
        response = confd.groups(group['id']).members.users.put(users=[])
        response.assert_updated()


@fixtures.group()
@fixtures.user()
@fixtures.user()
@fixtures.line_sip()
@fixtures.line_sip()
def test_delete_group_when_group_and_user_associated(group, user1, user2, line1, line2):
    with a.user_line(user1, line1), a.user_line(user2, line2), \
            a.group_member_user(group, user1, user2, check=False):
        confd.groups(group['id']).delete().assert_deleted()

        deleted_group = confd.groups(group['id']).get
        yield s.check_resource_not_found, deleted_group, 'Group'

        response = confd.users(user1['uuid']).get()
        yield assert_that, response.item['groups'], empty()

        response = confd.users(user2['uuid']).get()
        yield assert_that, response.item['groups'], empty()


@fixtures.group()
@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_delete_user_when_group_and_user_associated(group1, group2, user, line):
    with a.user_line(user, line, check=False), \
            a.group_member_user(group1, user, check=False), \
            a.group_member_user(group2, user, check=False):
        confd.lines(line['id']).delete().assert_deleted()
        confd.users(user['uuid']).delete().assert_deleted()

        deleted_user = confd.users(user['uuid']).get
        yield s.check_resource_not_found, deleted_user, 'User'

        response = confd.groups(group1['id']).get()
        yield assert_that, response.item['members']['users'], empty()

        response = confd.groups(group2['id']).get()
        yield assert_that, response.item['members']['users'], empty()


@fixtures.group()
@fixtures.user()
@fixtures.line_sip()
def test_bus_events(group, user, line):
    with a.user_line(user, line):
        url = confd.groups(group['id']).members.users.put
        body = {'users': [user]}
        yield s.check_bus_event, 'config.groups.members.users.updated', url, body
