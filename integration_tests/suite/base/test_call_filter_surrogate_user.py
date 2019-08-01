# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    empty,
    has_entries,
    is_not,
    none,
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
    with fixtures.call_filter() as call_filter, fixtures.user() as user:
        response = confd.callfilters(FAKE_ID).surrogates.users.put(users=[user])
        response.assert_status(404)

        url = confd.callfilters(call_filter['id']).surrogates.users.put
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
    with fixtures.call_filter() as call_filter, fixtures.user() as user:
        response = confd.callfilters(call_filter['id']).surrogates.users.put(users=[user])
        response.assert_updated()



def test_associate_multiple():
    with fixtures.call_filter() as call_filter, fixtures.user() as user1, fixtures.user() as user2, fixtures.user() as user3:
        response = confd.callfilters(call_filter['id']).surrogates.users.put(users=[user3, user1, user2])
        response.assert_updated()

        response = confd.callfilters(call_filter['id']).get()
        assert_that(response.item, has_entries(
            surrogates=has_entries(users=contains(
                has_entries(uuid=user3['uuid']),
                has_entries(uuid=user1['uuid']),
                has_entries(uuid=user2['uuid'])
            ))
        ))



def test_associate_same_user():
    with fixtures.call_filter() as call_filter, fixtures.user() as user:
        response = confd.callfilters(call_filter['id']).surrogates.users.put(users=[user, user])
        response.assert_status(400)



def test_associate_recipient_to_surrogate():
    with fixtures.call_filter() as call_filter, fixtures.user() as user:
        with a.call_filter_recipient_user(call_filter, user):
            response = confd.callfilters(call_filter['id']).surrogates.users.put(users=[user])
            response.assert_status(400)


def test_associate_multi_tenant():
    with fixtures.call_filter(wazo_tenant=MAIN_TENANT) as main_call_filter, fixtures.call_filter(wazo_tenant=SUB_TENANT) as sub_call_filter, fixtures.user(wazo_tenant=MAIN_TENANT) as main_user, fixtures.user(wazo_tenant=SUB_TENANT) as sub_user:
        response = confd.callfilters(main_call_filter['id']).surrogates.users.put(
            users=[{'uuid': main_user['uuid']}],
            wazo_tenant=SUB_TENANT,
        )
        response.assert_match(404, e.not_found('CallFilter'))

        response = confd.callfilters(sub_call_filter['id']).surrogates.users.put(
            users=[{'uuid': main_user['uuid']}],
            wazo_tenant=SUB_TENANT,
        )
        response.assert_match(400, e.not_found('User'))

        response = confd.callfilters(main_call_filter['id']).surrogates.users.put(
            users=[{'uuid': sub_user['uuid']}],
            wazo_tenant=MAIN_TENANT,
        )
        response.assert_match(400, e.different_tenant())



def test_get_users_associated_to_call_filter():
    with fixtures.call_filter() as call_filter, fixtures.user() as user1, fixtures.user() as user2:
        with a.call_filter_surrogate_user(call_filter, user2, user1):
            response = confd.callfilters(call_filter['id']).get()
            assert_that(response.item, has_entries(
                surrogates=has_entries(users=contains(
                    has_entries(
                        uuid=user2['uuid'],
                        firstname=user2['firstname'],
                        lastname=user2['lastname'],
                        member_id=is_not(none()),
                    ),
                    has_entries(
                        uuid=user1['uuid'],
                        firstname=user1['firstname'],
                        lastname=user1['lastname'],
                        member_id=is_not(none()),
                    ),
                ))
            ))


def test_dissociate():
    with fixtures.call_filter() as call_filter, fixtures.user() as user1, fixtures.user() as user2:
        with a.call_filter_surrogate_user(call_filter, user1, user2):
            response = confd.callfilters(call_filter['id']).surrogates.users.put(users=[])
            response.assert_updated()


def test_delete_call_filter_when_call_filter_and_user_associated():
    with fixtures.call_filter() as call_filter, fixtures.user() as user1, fixtures.user() as user2:
        with a.call_filter_surrogate_user(call_filter, user1, user2, check=False):
            confd.callfilters(call_filter['id']).delete().assert_deleted()

            deleted_call_filter = confd.callfilters(call_filter['id']).get
            s.check_resource_not_found(deleted_call_filter, 'CallFilter')

            # When the relation will be added,
            # we should check if users have the key.callfilters to empty


def test_delete_user_when_call_filter_and_user_associated():
    with fixtures.call_filter() as call_filter1, fixtures.call_filter() as call_filter2, fixtures.user() as user:
        with a.call_filter_surrogate_user(call_filter1, user, check=False), \
            a.call_filter_surrogate_user(call_filter2, user, check=False):
            confd.users(user['uuid']).delete().assert_deleted()

            response = confd.callfilters(call_filter1['id']).get()
            assert_that(response.item['surrogates']['users'], empty())

            response = confd.callfilters(call_filter2['id']).get()
            assert_that(response.item['surrogates']['users'], empty())


def test_bus_events():
    with fixtures.call_filter() as call_filter, fixtures.user() as user:
        url = confd.callfilters(call_filter['id']).surrogates.users.put
        body = {'users': [user]}
        s.check_bus_event('config.callfilters.surrogates.users.updated', url, body)

