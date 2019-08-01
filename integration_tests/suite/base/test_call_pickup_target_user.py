# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
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
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

FAKE_UUID = '99999999-9999-9999-9999-999999999999'


def test_associate_errors():
    with fixtures.call_pickup() as call_pickup, fixtures.user() as user:
        response = confd.callpickups(FAKE_UUID).targets.users.put(users=[user])
        response.assert_status(404)

        url = confd.callpickups(call_pickup['id']).targets.users.put
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


def test_associate():
    with fixtures.call_pickup() as call_pickup, fixtures.user() as user:
        response = confd.callpickups(call_pickup['id']).targets.users.put(users=[user])
        response.assert_updated()



def test_associate_multiple():
    with fixtures.call_pickup() as call_pickup, fixtures.user() as user1, fixtures.user() as user2, fixtures.user() as user3:
        response = confd.callpickups(call_pickup['id']).targets.users.put(users=[user1, user2, user3])
        response.assert_updated()

        response = confd.callpickups(call_pickup['id']).get()
        assert_that(response.item, has_entries(
            targets=has_entries(users=contains_inanyorder(
                has_entries(uuid=user1['uuid']),
                has_entries(uuid=user2['uuid']),
                has_entries(uuid=user3['uuid'])
            ))
        ))



def test_associate_same_user():
    with fixtures.call_pickup() as call_pickup, fixtures.user() as user:
        response = confd.callpickups(call_pickup['id']).targets.users.put(users=[user, user])
        response.assert_status(400)



def test_associate_multi_tenant():
    with fixtures.call_pickup(wazo_tenant=MAIN_TENANT) as main_call_pickup, fixtures.call_pickup(wazo_tenant=SUB_TENANT) as sub_call_pickup, fixtures.user(wazo_tenant=MAIN_TENANT) as main_user, fixtures.user(wazo_tenant=SUB_TENANT) as sub_user:
        response = (
            confd.callpickups(main_call_pickup['id'])
            .targets.users(users=[sub_user])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('CallPickup'))

        response = (
            confd.callpickups(sub_call_pickup['id'])
            .targets.users(users=[main_user])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(400, e.not_found('User'))

        response = (
            confd.callpickups(sub_call_pickup['id'])
            .interceptors.users(users=[main_user])
            .put(wazo_tenant=MAIN_TENANT)
        )
        response.assert_match(400, e.different_tenant())



def test_get_users_associated_to_call_pickup():
    with fixtures.call_pickup() as call_pickup, fixtures.user() as user1, fixtures.user() as user2:
        with a.call_pickup_target_user(call_pickup, user1, user2):
            response = confd.callpickups(call_pickup['id']).get()
            assert_that(response.item, has_entries(
                targets=has_entries(users=contains_inanyorder(
                    has_entries(
                        uuid=user1['uuid'],
                        firstname=user1['firstname'],
                        lastname=user1['lastname'],
                    ),
                    has_entries(
                        uuid=user2['uuid'],
                        firstname=user2['firstname'],
                        lastname=user2['lastname'],
                    ),
                ))
            ))


def test_dissociate():
    with fixtures.call_pickup() as call_pickup, fixtures.user() as user:
        with a.call_pickup_target_user(call_pickup, user):
            response = confd.callpickups(call_pickup['id']).targets.users.put(users=[])
            response.assert_updated()


def test_delete_call_pickup_when_call_pickup_and_user_associated():
    with fixtures.call_pickup() as call_pickup, fixtures.user() as user1, fixtures.user() as user2:
        with a.call_pickup_target_user(call_pickup, user1, user2, check=False):
            confd.callpickups(call_pickup['id']).delete().assert_deleted()

            deleted_call_pickup = confd.callpickups(call_pickup['id']).get
            s.check_resource_not_found(deleted_call_pickup, 'CallPickup')

            # When the relation will be added,
            # we should check if users have the key.callpickups to empty


def test_delete_user_when_call_pickup_and_user_associated():
    with fixtures.call_pickup() as call_pickup1, fixtures.call_pickup() as call_pickup2, fixtures.user() as user:
        with a.call_pickup_target_user(call_pickup1, user, check=False), \
            a.call_pickup_target_user(call_pickup2, user, check=False):
            confd.users(user['uuid']).delete().assert_deleted()

            response = confd.callpickups(call_pickup1['id']).get()
            assert_that(response.item['targets']['users'], empty())

            response = confd.callpickups(call_pickup2['id']).get()
            assert_that(response.item['targets']['users'], empty())


def test_bus_events():
    with fixtures.call_pickup() as call_pickup, fixtures.user() as user:
        url = confd.callpickups(call_pickup['id']).targets.users.put
        body = {'users': [user]}
        s.check_bus_event('config.callpickups.targets.users.updated', url, body)

