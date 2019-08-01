# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    empty,
    has_entries,
    not_,
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

FAKE_ID = 999999999


def test_associate_errors():
    with fixtures.user() as user, fixtures.call_permission() as call_permission:
        fake_user = confd.users(FAKE_ID).callpermissions(call_permission['id']).put
        fake_call_permission = confd.users(user['id']).callpermissions(FAKE_ID).put

        s.check_resource_not_found(fake_user, 'User')
        s.check_resource_not_found(fake_call_permission, 'CallPermission')



def test_dissociate_errors():
    with fixtures.user() as user, fixtures.call_permission() as call_permission:
        fake_user = confd.users(FAKE_ID).callpermissions(call_permission['id']).delete
        fake_call_permission = confd.users(user['id']).callpermissions(FAKE_ID).delete

        s.check_resource_not_found(fake_user, 'User')
        s.check_resource_not_found(fake_call_permission, 'CallPermission')



def test_get_errors():
    fake_user = confd.users(FAKE_ID).callpermissions.get
    fake_call_permission = confd.callpermissions(FAKE_ID).users.get

    s.check_resource_not_found(fake_user, 'User')
    s.check_resource_not_found(fake_call_permission, 'CallPermission')


def test_associate_user_call_permission():
    with fixtures.user() as user, fixtures.call_permission() as call_permission:
        response = confd.users(user['id']).callpermissions(call_permission['id']).put()
        response.assert_updated()



def test_associate_using_uuid():
    with fixtures.user() as user, fixtures.call_permission() as call_permission:
        response = confd.users(user['uuid']).callpermissions(call_permission['id']).put()
        response.assert_updated()



def test_associate_multiple_call_permissions_to_user():
    with fixtures.user() as user, fixtures.call_permission() as perm1, fixtures.call_permission() as perm2, fixtures.call_permission() as perm3:
        confd.users(user['id']).callpermissions(perm1['id']).put().assert_updated()
        confd.users(user['id']).callpermissions(perm2['id']).put().assert_updated()
        confd.users(user['id']).callpermissions(perm3['id']).put().assert_updated()



def test_associate_multiple_users_to_call_permission():
    with fixtures.user() as user1, fixtures.user() as user2, fixtures.user() as user3, fixtures.call_permission() as call_permission:
        confd.users(user1['id']).callpermissions(call_permission['id']).put().assert_updated()
        confd.users(user2['id']).callpermissions(call_permission['id']).put().assert_updated()
        confd.users(user3['id']).callpermissions(call_permission['id']).put().assert_updated()



def test_associate_multi_tenant():
    with fixtures.user(wazo_tenant=MAIN_TENANT) as main_user, fixtures.user(wazo_tenant=SUB_TENANT) as sub_user, fixtures.call_permission(wazo_tenant=MAIN_TENANT) as main_perm, fixtures.call_permission(wazo_tenant=SUB_TENANT) as sub_perm:
        response = confd.users(main_user['uuid']).callpermissions(sub_perm['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('User'))

        response = confd.users(sub_user['uuid']).callpermissions(main_perm['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('CallPermission'))

        response = confd.users(main_user['uuid']).callpermissions(sub_perm['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_get_call_permissions_associated_to_user():
    with fixtures.user() as user, fixtures.call_permission() as perm1, fixtures.call_permission() as perm2:
        with a.user_call_permission(user, perm1):
            with a.user_call_permission(user, perm2):
                response = confd.users(user['uuid']).get()
                assert_that(response.item, has_entries(
                    call_permissions=contains(
                        has_entries(
                            id=perm1['id'],
                            name=perm1['name'],
                        ),
                        has_entries(
                            id=perm2['id'],
                            name=perm2['name'],
                        ),
                    )
                ))

                # deprecated
                response = confd.users(user['id']).callpermissions.get()
                assert_that(response.items, contains(
                    has_entries({'user_id': user['id'], 'call_permission_id': perm1['id']}),
                    has_entries({'user_id': user['id'], 'call_permission_id': perm2['id']})
                ))

                response = confd.users(user['uuid']).callpermissions.get()
                assert_that(response.items, contains(
                    has_entries({'user_id': user['id'], 'call_permission_id': perm1['id']}),
                    has_entries({'user_id': user['id'], 'call_permission_id': perm2['id']})
                ))


def test_get_call_permission_after_dissociation():
    with fixtures.user() as user, fixtures.call_permission() as call_permission:
        h.user_call_permission.associate(user['id'], call_permission['id'])
        h.user_call_permission.dissociate(user['id'], call_permission['id'])

        response = confd.users(user['id']).callpermissions.get()
        assert_that(response.items, empty())

        response = confd.users(user['uuid']).callpermissions.get()
        assert_that(response.items, empty())



def test_get_users_associated_to_call_permission():
    with fixtures.user() as user1, fixtures.user() as user2, fixtures.call_permission() as call_permission:
        with a.user_call_permission(user1, call_permission):
            with a.user_call_permission(user2, call_permission):
                response = confd.callpermissions(call_permission['id']).get()
                assert_that(response.item, has_entries(
                    users=contains(
                        has_entries(
                            uuid=user1['uuid'],
                            firstname=user1['firstname'],
                            lastname=user2['lastname'],
                        ),
                        has_entries(
                            uuid=user2['uuid'],
                            firstname=user2['firstname'],
                            lastname=user2['lastname'],
                        ),
                    )
                ))

                # deprecated
                response = confd.callpermissions(call_permission['id']).users.get()
                assert_that(response.items, contains(
                    has_entries({'user_id': user1['id'], 'call_permission_id': call_permission['id']}),
                    has_entries({'user_id': user2['id'], 'call_permission_id': call_permission['id']})
                ))


def test_associate_when_user_already_associated_to_same_call_permission():
    with fixtures.user() as user, fixtures.call_permission() as call_permission:
        with a.user_call_permission(user, call_permission):
            response = confd.users(user['id']).callpermissions(call_permission['id']).put()
            response.assert_updated()


def test_dissociate_using_uuid():
    with fixtures.user() as user, fixtures.call_permission() as call_permission:
        with a.user_call_permission(user, call_permission, check=False):
            response = confd.users(user['uuid']).callpermissions(call_permission['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.user() as user, fixtures.call_permission() as call_permission:
        response = confd.users(user['uuid']).callpermissions(call_permission['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.user(wazo_tenant=MAIN_TENANT) as main_user, fixtures.user(wazo_tenant=SUB_TENANT) as sub_user, fixtures.call_permission(wazo_tenant=MAIN_TENANT) as main_perm, fixtures.call_permission(wazo_tenant=SUB_TENANT) as sub_perm:
        response = confd.users(main_user['uuid']).callpermissions(sub_perm['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('User'))

        response = confd.users(sub_user['uuid']).callpermissions(main_perm['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('CallPermission'))



def test_delete_user_when_user_and_call_permission_associated():
    with fixtures.user() as user, fixtures.call_permission() as call_permission:
        with a.user_call_permission(user, call_permission, check=False):
            response = confd.users(user['id']).callpermissions.get()
            assert_that(response.items, not_(empty()))
            confd.users(user['id']).delete().assert_deleted()
            invalid_user = confd.users(user['id']).callpermissions.get
            s.check_resource_not_found(invalid_user, 'User')


def test_delete_call_permission_when_user_and_call_permission_associated():
    with fixtures.user() as user, fixtures.call_permission() as call_permission:
        with a.user_call_permission(user, call_permission, check=False):
            response = confd.users(user['id']).callpermissions.get()
            assert_that(response.items, not_(empty()))
            confd.callpermissions(call_permission['id']).delete().assert_deleted()
            response = confd.users(user['id']).callpermissions.get()
            assert_that(response.items, empty())
