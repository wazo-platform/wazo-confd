# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains,
    has_entries,
    empty,
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


def test_associate_errors():
    with fixtures.outcall() as outcall, fixtures.call_permission() as call_permission:
        fake_outcall = confd.outcalls(FAKE_ID).callpermissions(call_permission['id']).put
        fake_call_permission = confd.outcalls(outcall['id']).callpermissions(FAKE_ID).put

        s.check_resource_not_found(fake_outcall, 'Outcall')
        s.check_resource_not_found(fake_call_permission, 'CallPermission')



def test_dissociate_errors():
    with fixtures.outcall() as outcall, fixtures.call_permission() as call_permission:
        fake_outcall = confd.outcalls(FAKE_ID).callpermissions(call_permission['id']).delete
        fake_call_permission = confd.outcalls(outcall['id']).callpermissions(FAKE_ID).delete

        s.check_resource_not_found(fake_outcall, 'Outcall')
        s.check_resource_not_found(fake_call_permission, 'CallPermission')



def test_associate():
    with fixtures.outcall() as outcall, fixtures.call_permission() as call_permission:
        response = confd.outcalls(outcall['id']).callpermissions(call_permission['id']).put()
        response.assert_updated()



def test_associate_multiple_call_permissions_to_outcall():
    with fixtures.outcall() as outcall, fixtures.call_permission() as perm1, fixtures.call_permission() as perm2, fixtures.call_permission() as perm3:
        confd.outcalls(outcall['id']).callpermissions(perm1['id']).put().assert_updated()
        confd.outcalls(outcall['id']).callpermissions(perm2['id']).put().assert_updated()
        confd.outcalls(outcall['id']).callpermissions(perm3['id']).put().assert_updated()



def test_associate_multiple_outcalls_to_call_permission():
    with fixtures.outcall() as outcall1, fixtures.outcall() as outcall2, fixtures.outcall() as outcall3, fixtures.call_permission() as call_permission:
        confd.outcalls(outcall1['id']).callpermissions(call_permission['id']).put().assert_updated()
        confd.outcalls(outcall2['id']).callpermissions(call_permission['id']).put().assert_updated()
        confd.outcalls(outcall3['id']).callpermissions(call_permission['id']).put().assert_updated()



def test_associate_when_outcall_already_associated_to_same_call_permission():
    with fixtures.outcall() as outcall, fixtures.call_permission() as call_permission:
        with a.outcall_call_permission(outcall, call_permission):
            response = confd.outcalls(outcall['id']).callpermissions(call_permission['id']).put()
            response.assert_updated()


def test_associate_multi_tenant():
    with fixtures.outcall(wazo_tenant=MAIN_TENANT) as main_outcall, fixtures.outcall(wazo_tenant=SUB_TENANT) as sub_outcall, fixtures.call_permission(wazo_tenant=MAIN_TENANT) as main_perm, fixtures.call_permission(wazo_tenant=SUB_TENANT) as sub_perm:
        response = confd.outcalls(main_outcall['id']).callpermissions(sub_perm['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Outcall'))

        response = confd.outcalls(sub_outcall['id']).callpermissions(main_perm['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('CallPermission'))

        response = confd.outcalls(main_outcall['id']).callpermissions(sub_perm['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_match(400, e.different_tenant())



def test_dissociate():
    with fixtures.outcall() as outcall, fixtures.call_permission() as call_permission:
        with a.outcall_call_permission(outcall, call_permission, check=False):
            response = confd.outcalls(outcall['id']).callpermissions(call_permission['id']).delete()
            response.assert_deleted()


def test_dissociate_not_associated():
    with fixtures.outcall() as outcall, fixtures.call_permission() as call_permission:
        response = confd.outcalls(outcall['id']).callpermissions(call_permission['id']).delete()
        response.assert_deleted()



def test_dissociate_multi_tenant():
    with fixtures.outcall(wazo_tenant=MAIN_TENANT) as main_outcall, fixtures.outcall(wazo_tenant=SUB_TENANT) as sub_outcall, fixtures.call_permission(wazo_tenant=MAIN_TENANT) as main_perm, fixtures.call_permission(wazo_tenant=SUB_TENANT) as sub_perm:
        response = confd.outcalls(main_outcall['id']).callpermissions(sub_perm['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Outcall'))

        response = confd.outcalls(sub_outcall['id']).callpermissions(main_perm['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('CallPermission'))



def test_get_call_permissions_relation():
    with fixtures.outcall() as outcall, fixtures.call_permission() as call_permission:
        with a.outcall_call_permission(outcall, call_permission):
            response = confd.outcalls(outcall['id']).get()
            assert_that(response.item['call_permissions'], contains(
                has_entries(id=call_permission['id'], name=call_permission['name'])
            ))


def test_get_outcalls_relation():
    with fixtures.outcall() as outcall, fixtures.call_permission() as call_permission:
        with a.outcall_call_permission(outcall, call_permission):
            response = confd.callpermissions(call_permission['id']).get()
            assert_that(response.item['outcalls'], contains(
                has_entries(id=outcall['id'], name=outcall['name'])
            ))


def test_delete_outcall_when_outcall_and_call_permission_associated():
    with fixtures.outcall() as outcall, fixtures.call_permission() as call_permission:
        with a.outcall_call_permission(outcall, call_permission, check=False):
            confd.outcalls(outcall['id']).delete().assert_deleted()
            response = confd.callpermissions(call_permission['id']).get()
            assert_that(response.item['outcalls'], empty())


def test_delete_call_permission_when_outcall_and_call_permission_associated():
    with fixtures.outcall() as outcall, fixtures.call_permission() as call_permission:
        with a.outcall_call_permission(outcall, call_permission, check=False):
            confd.callpermissions(call_permission['id']).delete().assert_deleted()
            response = confd.outcalls(outcall['id']).get()
            assert_that(response.item['call_permissions'], empty())


def test_bus_events():
    with fixtures.outcall() as outcall, fixtures.call_permission() as call_permission:
        yield (s.check_bus_event,
               'config.outcalls.{}.callpermissions.updated'.format(outcall['id']),
               confd.outcalls(outcall['id']).callpermissions(call_permission['id']).put)
        yield (s.check_bus_event,
               'config.outcalls.{}.callpermissions.deleted'.format(outcall['id']),
               confd.outcalls(outcall['id']).callpermissions(call_permission['id']).delete)

