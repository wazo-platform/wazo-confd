# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    contains,
    has_entries,
    empty,
)

from ..helpers import (
    associations as a,
    fixtures,
    scenarios as s,
)
from . import confd


FAKE_ID = 999999999


@fixtures.outcall()
@fixtures.call_permission()
def test_associate_errors(outcall, call_permission):
    fake_outcall = confd.outcalls(FAKE_ID).callpermissions(call_permission['id']).put
    fake_call_permission = confd.outcalls(outcall['id']).callpermissions(FAKE_ID).put

    yield s.check_resource_not_found, fake_outcall, 'Outcall'
    yield s.check_resource_not_found, fake_call_permission, 'CallPermission'


@fixtures.outcall()
@fixtures.call_permission()
def test_dissociate_errors(outcall, call_permission):
    fake_outcall = confd.outcalls(FAKE_ID).callpermissions(call_permission['id']).delete
    fake_call_permission = confd.outcalls(outcall['id']).callpermissions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_outcall, 'Outcall'
    yield s.check_resource_not_found, fake_call_permission, 'CallPermission'


@fixtures.outcall()
@fixtures.call_permission()
def test_associate(outcall, call_permission):
    response = confd.outcalls(outcall['id']).callpermissions(call_permission['id']).put()
    response.assert_updated()


@fixtures.outcall()
@fixtures.call_permission()
@fixtures.call_permission()
@fixtures.call_permission()
def test_associate_multiple_call_permissions_to_outcall(outcall, perm1, perm2, perm3):
    confd.outcalls(outcall['id']).callpermissions(perm1['id']).put().assert_updated()
    confd.outcalls(outcall['id']).callpermissions(perm2['id']).put().assert_updated()
    confd.outcalls(outcall['id']).callpermissions(perm3['id']).put().assert_updated()


@fixtures.outcall()
@fixtures.outcall()
@fixtures.outcall()
@fixtures.call_permission()
def test_associate_multiple_outcalls_to_call_permission(outcall1, outcall2, outcall3, call_permission):
    confd.outcalls(outcall1['id']).callpermissions(call_permission['id']).put().assert_updated()
    confd.outcalls(outcall2['id']).callpermissions(call_permission['id']).put().assert_updated()
    confd.outcalls(outcall3['id']).callpermissions(call_permission['id']).put().assert_updated()


@fixtures.outcall()
@fixtures.call_permission()
def test_associate_when_outcall_already_associated_to_same_call_permission(outcall, call_permission):
    with a.outcall_call_permission(outcall, call_permission):
        response = confd.outcalls(outcall['id']).callpermissions(call_permission['id']).put()
        response.assert_updated()


@fixtures.outcall()
@fixtures.call_permission()
def test_dissociate(outcall, call_permission):
    with a.outcall_call_permission(outcall, call_permission, check=False):
        response = confd.outcalls(outcall['id']).callpermissions(call_permission['id']).delete()
        response.assert_deleted()


@fixtures.outcall()
@fixtures.call_permission()
def test_dissociate_not_associated(outcall, call_permission):
    response = confd.outcalls(outcall['id']).callpermissions(call_permission['id']).delete()
    response.assert_deleted()


@fixtures.outcall()
@fixtures.call_permission()
def test_get_call_permissions_relation(outcall, call_permission):
    with a.outcall_call_permission(outcall, call_permission):
        response = confd.outcalls(outcall['id']).get()
        assert_that(response.item['call_permissions'], contains(
            has_entries(id=call_permission['id'],
                        name=call_permission['name'])
        ))


@fixtures.outcall()
@fixtures.call_permission()
def test_get_outcalls_relation(outcall, call_permission):
    with a.outcall_call_permission(outcall, call_permission):
        response = confd.callpermissions(call_permission['id']).get()
        assert_that(response.item['outcalls'], contains(
            has_entries(id=outcall['id'],
                        name=outcall['name'])
        ))


@fixtures.outcall()
@fixtures.call_permission()
def test_delete_outcall_when_outcall_and_call_permission_associated(outcall, call_permission):
    with a.outcall_call_permission(outcall, call_permission, check=False):
        confd.outcalls(outcall['id']).delete().assert_deleted()
        response = confd.callpermissions(call_permission['id']).get()
        assert_that(response.item['outcalls'], empty())


@fixtures.outcall()
@fixtures.call_permission()
def test_delete_call_permission_when_outcall_and_call_permission_associated(outcall, call_permission):
    with a.outcall_call_permission(outcall, call_permission, check=False):
        confd.callpermissions(call_permission['id']).delete().assert_deleted()
        response = confd.outcalls(outcall['id']).get()
        assert_that(response.item['call_permissions'], empty())


@fixtures.outcall()
@fixtures.call_permission()
def test_bus_events(outcall, call_permission):
    yield (s.check_bus_event,
           'config.outcalls.{}.callpermissions.updated'.format(outcall['id']),
           confd.outcalls(outcall['id']).callpermissions(call_permission['id']).put)
    yield (s.check_bus_event,
           'config.outcalls.{}.callpermissions.deleted'.format(outcall['id']),
           confd.outcalls(outcall['id']).callpermissions(call_permission['id']).delete)
