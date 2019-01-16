# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
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


@fixtures.user()
@fixtures.call_permission()
def test_associate_errors(user, call_permission):
    fake_user = confd.users(FAKE_ID).callpermissions(call_permission['id']).put
    fake_call_permission = confd.users(user['id']).callpermissions(FAKE_ID).put

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_call_permission, 'CallPermission'


@fixtures.user()
@fixtures.call_permission()
def test_dissociate_errors(user, call_permission):
    fake_user = confd.users(FAKE_ID).callpermissions(call_permission['id']).delete
    fake_call_permission = confd.users(user['id']).callpermissions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_call_permission, 'CallPermission'


def test_get_errors():
    fake_user = confd.users(FAKE_ID).callpermissions.get
    fake_call_permission = confd.callpermissions(FAKE_ID).users.get

    yield s.check_resource_not_found, fake_user, 'User'
    yield s.check_resource_not_found, fake_call_permission, 'CallPermission'


@fixtures.user()
@fixtures.call_permission()
def test_associate_user_call_permission(user, call_permission):
    response = confd.users(user['id']).callpermissions(call_permission['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.call_permission()
def test_associate_using_uuid(user, call_permission):
    response = confd.users(user['uuid']).callpermissions(call_permission['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.call_permission()
@fixtures.call_permission()
@fixtures.call_permission()
def test_associate_multiple_call_permissions_to_user(user, perm1, perm2, perm3):
    confd.users(user['id']).callpermissions(perm1['id']).put().assert_updated()
    confd.users(user['id']).callpermissions(perm2['id']).put().assert_updated()
    confd.users(user['id']).callpermissions(perm3['id']).put().assert_updated()


@fixtures.user()
@fixtures.user()
@fixtures.user()
@fixtures.call_permission()
def test_associate_multiple_users_to_call_permission(user1, user2, user3, call_permission):
    confd.users(user1['id']).callpermissions(call_permission['id']).put().assert_updated()
    confd.users(user2['id']).callpermissions(call_permission['id']).put().assert_updated()
    confd.users(user3['id']).callpermissions(call_permission['id']).put().assert_updated()


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
@fixtures.call_permission(wazo_tenant=MAIN_TENANT)
@fixtures.call_permission(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_user, sub_user, main_perm, sub_perm):
    response = confd.users(main_user['uuid']).callpermissions(sub_perm['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('User'))

    response = confd.users(sub_user['uuid']).callpermissions(main_perm['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('CallPermission'))

    response = confd.users(main_user['uuid']).callpermissions(sub_perm['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.user()
@fixtures.call_permission()
@fixtures.call_permission()
def test_get_call_permissions_associated_to_user(user, perm1, perm2):
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


@fixtures.user()
@fixtures.call_permission()
def test_get_call_permission_after_dissociation(user, call_permission):
    h.user_call_permission.associate(user['id'], call_permission['id'])
    h.user_call_permission.dissociate(user['id'], call_permission['id'])

    response = confd.users(user['id']).callpermissions.get()
    assert_that(response.items, empty())

    response = confd.users(user['uuid']).callpermissions.get()
    assert_that(response.items, empty())


@fixtures.user()
@fixtures.user()
@fixtures.call_permission()
def test_get_users_associated_to_call_permission(user1, user2, call_permission):
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


@fixtures.user()
@fixtures.call_permission()
def test_associate_when_user_already_associated_to_same_call_permission(user, call_permission):
    with a.user_call_permission(user, call_permission):
        response = confd.users(user['id']).callpermissions(call_permission['id']).put()
        response.assert_updated()


@fixtures.user()
@fixtures.call_permission()
def test_dissociate_using_uuid(user, call_permission):
    with a.user_call_permission(user, call_permission, check=False):
        response = confd.users(user['uuid']).callpermissions(call_permission['id']).delete()
        response.assert_deleted()


@fixtures.user()
@fixtures.call_permission()
def test_dissociate_not_associated(user, call_permission):
    response = confd.users(user['uuid']).callpermissions(call_permission['id']).delete()
    response.assert_deleted()


@fixtures.user(wazo_tenant=MAIN_TENANT)
@fixtures.user(wazo_tenant=SUB_TENANT)
@fixtures.call_permission(wazo_tenant=MAIN_TENANT)
@fixtures.call_permission(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_user, sub_user, main_perm, sub_perm):
    response = confd.users(main_user['uuid']).callpermissions(sub_perm['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('User'))

    response = confd.users(sub_user['uuid']).callpermissions(main_perm['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found('CallPermission'))


@fixtures.user()
@fixtures.call_permission()
def test_delete_user_when_user_and_call_permission_associated(user, call_permission):
    with a.user_call_permission(user, call_permission, check=False):
        response = confd.users(user['id']).callpermissions.get()
        assert_that(response.items, not_(empty()))
        confd.users(user['id']).delete().assert_deleted()
        invalid_user = confd.users(user['id']).callpermissions.get
        yield s.check_resource_not_found, invalid_user, 'User'


@fixtures.user()
@fixtures.call_permission()
def test_delete_call_permission_when_user_and_call_permission_associated(user, call_permission):
    with a.user_call_permission(user, call_permission, check=False):
        response = confd.users(user['id']).callpermissions.get()
        assert_that(response.items, not_(empty()))
        confd.callpermissions(call_permission['id']).delete().assert_deleted()
        response = confd.users(user['id']).callpermissions.get()
        assert_that(response.items, empty())
