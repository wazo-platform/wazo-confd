# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    empty,
    has_entries,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    helpers as h,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_UUID = 'uuid-not-found'


@fixtures.switchboard()
@fixtures.user()
def test_associate_errors(switchboard, user):
    users = [{'uuid': user['uuid']}]
    response = confd.switchboards(FAKE_UUID).members.users.put(users=users)
    response.assert_status(404)

    url = confd.switchboards(switchboard['uuid']).members.users.put

    s.check_missing_required_field_returns_error(url, 'users')
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


@fixtures.switchboard()
@fixtures.user()
def test_associate(switchboard, user):
    users = [{'uuid': user['uuid']}]
    response = confd.switchboards(switchboard['uuid']).members.users.put(users=users)
    response.assert_updated()


@fixtures.switchboard()
@fixtures.user()
def test_associate_same_user_twice(switchboard, user):
    users = [{'uuid': user['uuid']}, {'uuid': user['uuid']}]
    response = confd.switchboards(switchboard['uuid']).members.users.put(users=users)
    response.assert_updated()


@fixtures.switchboard(wazo_tenant=MAIN_TENANT)
@fixtures.switchboard(wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_switchboard, sub_switchboard, main_user, sub_user):
    response = (
        confd.switchboards(main_switchboard['uuid'])
        .members.users(users=[sub_user])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Switchboard'))

    response = (
        confd.switchboards(sub_switchboard['uuid'])
        .members.users(users=[main_user])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(400, e.not_found('User'))

    response = (
        confd.switchboards(sub_switchboard['uuid'])
        .members.users(users=[main_user])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(400, e.different_tenant())


@fixtures.switchboard()
@fixtures.user()
@fixtures.user()
def test_get_users_associated_to_switchboard(switchboard, user1, user2):
    with (a.switchboard_member_user(switchboard, [user1, user2])):
        response = confd.switchboards(switchboard['uuid']).get()
        assert_that(response.item, has_entries(
            members=has_entries(users=contains_inanyorder(
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
            ))
        ))


@fixtures.switchboard()
@fixtures.switchboard()
@fixtures.user()
def test_get_switchboards_associated_to_user(switchboard1, switchboard2, user):
    with a.switchboard_member_user(switchboard1, [user]), \
         a.switchboard_member_user(switchboard2, [user]):
        response = confd.users(user['uuid']).get()
        assert_that(response.item, has_entries(
            switchboards=contains_inanyorder(
                has_entries(uuid=switchboard1['uuid'], name=switchboard1['name']),
                has_entries(uuid=switchboard2['uuid'], name=switchboard2['name']),
            )
        ))


@fixtures.switchboard()
@fixtures.user()
@fixtures.user()
def test_delete_switchboard_when_switchboard_and_user_associated(switchboard, user1, user2):
    h.switchboard_member_user.associate(switchboard['uuid'], [user1['uuid'], user2['uuid']])

    confd.switchboards(switchboard['uuid']).delete().assert_deleted()


@fixtures.switchboard()
@fixtures.switchboard()
@fixtures.user()
def test_delete_user_when_switchboard_and_user_associated(switchboard1, switchboard2, user):
    with a.switchboard_member_user(switchboard2, [user]), \
         a.switchboard_member_user(switchboard1, [user]):
        confd.users(user['uuid']).delete().assert_deleted()

        response = confd.switchboards(switchboard1['uuid']).get()
        assert_that(response.item['members']['users'], empty())

        response = confd.switchboards(switchboard2['uuid']).get()
        assert_that(response.item['members']['users'], empty())


@fixtures.switchboard()
@fixtures.user()
def test_bus_events(switchboard, user):
    url = confd.switchboards(switchboard['uuid']).members.users.put
    body = {'users': [{'uuid': user['uuid']}]}
    routing_key = 'config.switchboards.{}.members.users.updated'.format(switchboard['uuid'])
    s.check_bus_event(routing_key, url, body)
