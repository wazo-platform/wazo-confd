# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains, empty, has_entries

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

FAKE_ID = 999999999


@fixtures.group()
@fixtures.call_permission()
def test_associate_errors(group, call_permission):
    fake_group = confd.groups(FAKE_ID).callpermissions(call_permission['id']).put
    fake_call_permission = confd.groups(group['id']).callpermissions(FAKE_ID).put

    s.check_resource_not_found(fake_group, 'Group')
    s.check_resource_not_found(fake_call_permission, 'CallPermission')

    fake_call_permission = confd.groups(group['uuid']).callpermissions(FAKE_ID).put
    s.check_resource_not_found(fake_call_permission, 'CallPermission')


@fixtures.group()
@fixtures.call_permission()
def test_dissociate_errors(group, call_permission):
    fake_group = confd.groups(FAKE_ID).callpermissions(call_permission['id']).delete
    fake_call_permission = confd.groups(group['id']).callpermissions(FAKE_ID).delete

    s.check_resource_not_found(fake_group, 'Group')
    s.check_resource_not_found(fake_call_permission, 'CallPermission')

    fake_call_permission = confd.groups(group['uuid']).callpermissions(FAKE_ID).delete
    s.check_resource_not_found(fake_call_permission, 'CallPermission')


@fixtures.group()
@fixtures.call_permission()
def test_associate(group, call_permission):
    response = confd.groups(group['id']).callpermissions(call_permission['id']).put()
    response.assert_updated()

    response = confd.groups(group['uuid']).callpermissions(call_permission['id']).put()
    response.assert_updated()


@fixtures.group()
@fixtures.call_permission()
@fixtures.call_permission()
@fixtures.call_permission()
def test_associate_multiple_call_permissions_to_group(group, perm1, perm2, perm3):
    confd.groups(group['uuid']).callpermissions(perm1['id']).put().assert_updated()
    confd.groups(group['uuid']).callpermissions(perm2['id']).put().assert_updated()
    confd.groups(group['id']).callpermissions(perm3['id']).put().assert_updated()


@fixtures.group()
@fixtures.group()
@fixtures.group()
@fixtures.call_permission()
def test_associate_multiple_groups_to_call_permission(
    group1, group2, group3, call_permission
):
    confd.groups(group1['uuid']).callpermissions(
        call_permission['id']
    ).put().assert_updated()
    confd.groups(group2['uuid']).callpermissions(
        call_permission['id']
    ).put().assert_updated()
    confd.groups(group3['id']).callpermissions(
        call_permission['id']
    ).put().assert_updated()


@fixtures.group()
@fixtures.call_permission()
def test_associate_when_group_already_associated_to_same_call_permission(
    group, call_permission
):
    with a.group_call_permission(group, call_permission):
        response = (
            confd.groups(group['id']).callpermissions(call_permission['id']).put()
        )
        response.assert_updated()

    with a.group_call_permission(group, call_permission):
        response = (
            confd.groups(group['uuid']).callpermissions(call_permission['id']).put()
        )
        response.assert_updated()


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.call_permission(wazo_tenant=MAIN_TENANT)
@fixtures.call_permission(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_group, sub_group, main_perm, sub_perm):
    response = (
        confd.groups(main_group['uuid'])
        .callpermissions(sub_perm['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Group'))

    response = (
        confd.groups(sub_group['uuid'])
        .callpermissions(main_perm['id'])
        .put(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('CallPermission'))

    response = (
        confd.groups(main_group['uuid'])
        .callpermissions(sub_perm['id'])
        .put(wazo_tenant=MAIN_TENANT)
    )
    response.assert_match(400, e.different_tenant())


@fixtures.group()
@fixtures.call_permission()
def test_dissociate(group, call_permission):
    with a.group_call_permission(group, call_permission, check=False):
        response = (
            confd.groups(group['uuid']).callpermissions(call_permission['id']).delete()
        )
        response.assert_deleted()

    with a.group_call_permission(group, call_permission, check=False):
        response = (
            confd.groups(group['id']).callpermissions(call_permission['id']).delete()
        )
        response.assert_deleted()


@fixtures.group(wazo_tenant=MAIN_TENANT)
@fixtures.group(wazo_tenant=SUB_TENANT)
@fixtures.call_permission(wazo_tenant=MAIN_TENANT)
@fixtures.call_permission(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_group, sub_group, main_perm, sub_perm):
    response = (
        confd.groups(main_group['uuid'])
        .callpermissions(sub_perm['id'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('Group'))

    response = (
        confd.groups(sub_group['uuid'])
        .callpermissions(main_perm['id'])
        .delete(wazo_tenant=SUB_TENANT)
    )
    response.assert_match(404, e.not_found('CallPermission'))


@fixtures.group()
@fixtures.call_permission()
def test_get_call_permissions_relation(group, call_permission):
    with a.group_call_permission(group, call_permission):
        response = confd.groups(group['uuid']).get()
        assert_that(
            response.item['call_permissions'],
            contains(
                has_entries(id=call_permission['id'], name=call_permission['name'])
            ),
        )


@fixtures.group()
@fixtures.call_permission()
def test_get_groups_relation(group, call_permission):
    with a.group_call_permission(group, call_permission):
        response = confd.callpermissions(call_permission['id']).get()
        assert_that(
            response.item['groups'],
            contains(
                has_entries(uuid=group['uuid'], id=group['id'], name=group['name'])
            ),
        )


@fixtures.group()
@fixtures.call_permission()
def test_delete_group_when_group_and_call_permission_associated(group, call_permission):
    with a.group_call_permission(group, call_permission, check=False):
        confd.groups(group['uuid']).delete().assert_deleted()
        response = confd.callpermissions(call_permission['id']).get()
        assert_that(response.item['groups'], empty())


@fixtures.group()
@fixtures.call_permission()
def test_delete_call_permission_when_group_and_call_permission_associated(
    group, call_permission
):
    with a.group_call_permission(group, call_permission, check=False):
        confd.callpermissions(call_permission['id']).delete().assert_deleted()
        response = confd.groups(group['id']).get()
        assert_that(response.item['call_permissions'], empty())


@fixtures.group()
@fixtures.call_permission()
def test_delete_call_permission_when_group_and_call_permission_associated_by_uuid(
    group, call_permission
):
    with a.group_call_permission(group, call_permission, check=False):
        confd.callpermissions(call_permission['id']).delete().assert_deleted()
        response = confd.groups(group['uuid']).get()
        assert_that(response.item['call_permissions'], empty())


@fixtures.group()
@fixtures.call_permission()
def test_bus_events(group, call_permission):
    headers = {'tenant_uuid': group['tenant_uuid']}

    s.check_event(
        'group_call_permission_associated',
        headers,
        confd.groups(group['uuid']).callpermissions(call_permission['id']).put,
    )
    s.check_event(
        'group_call_permission_dissociated',
        headers,
        confd.groups(group['uuid']).callpermissions(call_permission['id']).delete,
    )
