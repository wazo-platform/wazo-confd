# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
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


def test_associate_errors():
    with fixtures.group() as group, fixtures.user() as user:
        response = confd.groups(FAKE_ID).members.users.put(users=[user])
        response.assert_status(404)

        url = confd.groups(group['id']).members.users.put
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
    s.check_bogus_field_returns_error_matching_regex(url, 'users', [{'priority': None}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'users', [{'priority': 'string'}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'users', [{'priority': -1}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'users', [{'priority': []}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'users', [{'priority': {}}], regex)


def test_associate():
    with fixtures.group() as group, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            response = confd.groups(group['id']).members.users.put(users=[user])
            response.assert_updated()


def test_associate_multiple_with_priority():
    with fixtures.group() as group, fixtures.user() as user1, fixtures.user() as user2, fixtures.user() as user3, fixtures.line_sip() as line1, fixtures.line_sip() as line2, fixtures.line_sip() as line3:
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


def test_associate_user_with_no_line():
    with fixtures.group() as group, fixtures.user() as user:
        response = confd.groups(group['id']).members.users.put(users=[user])
        response.assert_match(400, e.missing_association('User', 'Line'))



def test_associate_same_user():
    with fixtures.group() as group, fixtures.user() as user, fixtures.line_sip() as line1, fixtures.line_sip() as line2:
        with a.user_line(user, line1), a.user_line(user, line2):
            response = confd.groups(group['id']).members.users.put(users=[user, user])
            response.assert_status(400)


def test_associate_multiple_user_with_same_line():
    with fixtures.group() as group, fixtures.user() as user1, fixtures.user() as user2, fixtures.line_sip() as line:
        with a.user_line(user1, line), a.user_line(user2, line):
            response = confd.groups(group['id']).members.users.put(users=[user1, user2])
            response.assert_match(400, re.compile('Cannot associate different users with the same line'))


def test_get_users_associated_to_group():
    with fixtures.group() as group, fixtures.user() as user1, fixtures.user() as user2, fixtures.line_sip() as line1, fixtures.line_sip() as line2:
        with a.user_line(user1, line1), a.user_line(user2, line2), \
            a.group_member_user(group, user2, user1):
            response = confd.groups(group['id']).get()
            assert_that(response.item, has_entries(
                members=has_entries(users=contains_inanyorder(
                    has_entries(uuid=user2['uuid'], firstname=user2['firstname'], lastname=user2['lastname']),
                    has_entries(uuid=user1['uuid'], firstname=user1['firstname'], lastname=user1['lastname']),
                ))
            ))


def test_get_groups_associated_to_user():
    with fixtures.group() as group1, fixtures.group() as group2, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line), a.group_member_user(group2, user), a.group_member_user(group1, user):
            response = confd.users(user['uuid']).get()
            assert_that(response.item, has_entries(
                groups=contains_inanyorder(
                    has_entries(id=group2['id'], name=group2['name']),
                    has_entries(id=group1['id'], name=group1['name']),
                )
            ))


def test_associate_multi_tenant():
    with fixtures.group(wazo_tenant=MAIN_TENANT) as main_group, fixtures.group(wazo_tenant=SUB_TENANT) as sub_group, fixtures.user(wazo_tenant=MAIN_TENANT) as main_user, fixtures.user(wazo_tenant=SUB_TENANT) as sub_user:
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



def test_dissociate():
    with fixtures.group() as group, fixtures.user() as user1, fixtures.user() as user2, fixtures.line_sip() as line1, fixtures.line_sip() as line2:
        with a.user_line(user1, line1), a.user_line(user2, line2), a.group_member_user(group, user1, user2):
            response = confd.groups(group['id']).members.users.put(users=[])
            response.assert_updated()


def test_delete_group_when_group_and_user_associated():
    with fixtures.group() as group, fixtures.user() as user1, fixtures.user() as user2, fixtures.line_sip() as line1, fixtures.line_sip() as line2:
        with a.user_line(user1, line1), a.user_line(user2, line2), \
            a.group_member_user(group, user1, user2, check=False):
            confd.groups(group['id']).delete().assert_deleted()

            deleted_group = confd.groups(group['id']).get
            s.check_resource_not_found(deleted_group, 'Group')

            response = confd.users(user1['uuid']).get()
            assert_that(response.item['groups'], empty())

            response = confd.users(user2['uuid']).get()
            assert_that(response.item['groups'], empty())


def test_delete_user_when_group_and_user_associated():
    with fixtures.group() as group1, fixtures.group() as group2, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line, check=False), \
            a.group_member_user(group1, user, check=False), \
            a.group_member_user(group2, user, check=False):
            confd.lines(line['id']).delete().assert_deleted()
            confd.users(user['uuid']).delete().assert_deleted()

            deleted_user = confd.users(user['uuid']).get
            s.check_resource_not_found(deleted_user, 'User')

            response = confd.groups(group1['id']).get()
            assert_that(response.item['members']['users'], empty())

            response = confd.groups(group2['id']).get()
            assert_that(response.item['members']['users'], empty())


def test_bus_events():
    with fixtures.group() as group, fixtures.user() as user, fixtures.line_sip() as line:
        with a.user_line(user, line):
            url = confd.groups(group['id']).members.users.put
            body = {'users': [user]}
            s.check_bus_event('config.groups.members.users.updated', url, body)
