# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains_inanyorder, empty, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

FAKE_ID = 999999999
FAKE_UUID = '99999999-9999-9999-9999-999999999999'


@fixtures.paging()
@fixtures.user()
def test_associate_errors(paging, user):
    response = confd.pagings(FAKE_ID).callers.users.put(users=[user])
    response.assert_status(404)

    url = confd.pagings(paging['id']).callers.users
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


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


@fixtures.paging()
@fixtures.user()
def test_associate(paging, user):
    response = confd.pagings(paging['id']).callers.users.put(users=[user])
    response.assert_updated()


@fixtures.paging()
@fixtures.user()
@fixtures.user()
@fixtures.user()
def test_associate_multiple(paging, user1, user2, user3):
    response = confd.pagings(paging['id']).callers.users.put(
        users=[user1, user2, user3]
    )
    response.assert_updated()

    response = confd.pagings(paging['id']).get()
    assert_that(
        response.item,
        has_entries(
            callers=has_entries(
                users=contains_inanyorder(
                    has_entries(uuid=user1['uuid']),
                    has_entries(uuid=user2['uuid']),
                    has_entries(uuid=user3['uuid']),
                )
            )
        ),
    )


@fixtures.paging()
@fixtures.user()
def test_associate_same_user(paging, user):
    response = confd.pagings(paging['id']).callers.users.put(users=[user, user])
    response.assert_status(400)


@fixtures.paging()
@fixtures.user()
@fixtures.user()
def test_get_users_associated_to_paging(paging, user1, user2):
    with a.paging_caller_user(paging, user2, user1):
        response = confd.pagings(paging['id']).get()
        assert_that(
            response.item,
            has_entries(
                callers=has_entries(
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


@fixtures.paging(wazo_tenant=MAIN_TENANT)
@fixtures.paging(wazo_tenant=SUB_TENANT)
@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_paging, sub_paging, main_user, sub_user):
    response = confd.pagings(main_paging['id']).callers.users.put(
        users=[{'uuid': main_user['uuid']}], wazo_tenant=SUB_TENANT
    )
    response.assert_match(404, e.not_found('Paging'))

    response = confd.pagings(sub_paging['id']).callers.users.put(
        users=[{'uuid': main_user['uuid']}], wazo_tenant=SUB_TENANT
    )
    response.assert_match(400, e.not_found('User'))

    response = confd.pagings(main_paging['id']).callers.users.put(
        users=[{'uuid': sub_user['uuid']}], wazo_tenant=MAIN_TENANT
    )
    response.assert_match(400, e.different_tenant())


@fixtures.paging()
@fixtures.user()
@fixtures.user()
def test_dissociate(paging, user1, user2):
    with a.paging_caller_user(paging, user1, user2):
        response = confd.pagings(paging['id']).callers.users.put(users=[])
        response.assert_updated()


@fixtures.paging()
@fixtures.user()
@fixtures.user()
def test_delete_paging_when_paging_and_user_associated(paging, user1, user2):
    with a.paging_caller_user(paging, user1, user2, check=False):
        confd.pagings(paging['id']).delete().assert_deleted()

        deleted_paging = confd.pagings(paging['id']).get
        s.check_resource_not_found(deleted_paging, 'Paging')

        # When the relation will be added,
        # we should check if users have the key pagings to empty


@fixtures.paging()
@fixtures.paging()
@fixtures.user()
def test_delete_user_when_paging_and_user_associated(paging1, paging2, user):
    with a.paging_caller_user(paging1, user, check=False), a.paging_caller_user(
        paging2, user, check=False
    ):
        confd.users(user['uuid']).delete().assert_deleted()

        response = confd.pagings(paging1['id']).get()
        assert_that(response.item['callers']['users'], empty())

        response = confd.pagings(paging2['id']).get()
        assert_that(response.item['callers']['users'], empty())


@fixtures.paging()
@fixtures.user()
def test_bus_events(paging, user):
    url = confd.pagings(paging['id']).callers.users.put
    body = {'users': [user]}
    headers = {'tenant_uuid': paging['tenant_uuid']}

    s.check_event('paging_caller_users_associated', headers, url, body)
