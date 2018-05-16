# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    contains,
    empty,
    has_entries,
)

from . import confd
from ..helpers import (
    associations as a,
    fixtures,
    scenarios as s,
)

FAKE_UUID = '99999999-9999-9999-9999-999999999999'


@fixtures.call_pickup()
@fixtures.user()
def test_associate_errors(call_pickup, user):
    response = confd.callpickups(FAKE_UUID).interceptors.users.put(users=[user])
    response.assert_status(404)

    url = confd.callpickups(call_pickup['id']).interceptors.users.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'users', 123
    yield s.check_bogus_field_returns_error, url, 'users', None
    yield s.check_bogus_field_returns_error, url, 'users', True
    yield s.check_bogus_field_returns_error, url, 'users', 'string'
    yield s.check_bogus_field_returns_error, url, 'users', [123]
    yield s.check_bogus_field_returns_error, url, 'users', [None]
    yield s.check_bogus_field_returns_error, url, 'users', ['string']
    yield s.check_bogus_field_returns_error, url, 'users', [{}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'uuid': None}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'uuid': 1}, {'uuid': None}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'not_uuid': 123}]
    yield s.check_bogus_field_returns_error, url, 'users', [{'uuid': FAKE_UUID}]


@fixtures.call_pickup()
@fixtures.user()
def test_associate(call_pickup, user):
    response = confd.callpickups(call_pickup['id']).interceptors.users.put(users=[user])
    response.assert_updated()


@fixtures.call_pickup()
@fixtures.user()
@fixtures.user()
@fixtures.user()
def test_associate_multiple(call_pickup, user1, user2, user3):
    response = confd.callpickups(call_pickup['id']).interceptors.users.put(users=[user1, user2, user3])
    response.assert_updated()


@fixtures.call_pickup()
@fixtures.user()
def test_associate_same_user(call_pickup, user):
    response = confd.callpickups(call_pickup['id']).interceptors.users.put(users=[user, user])
    response.assert_status(400)


@fixtures.call_pickup()
@fixtures.user()
def test_dissociate(call_pickup, user):
    with a.call_pickup_interceptor_user(call_pickup, user):
        response = confd.callpickups(call_pickup['id']).interceptors.users.put(users=[])
        response.assert_updated()


@fixtures.call_pickup()
@fixtures.user()
@fixtures.user()
def test_delete_call_pickup_when_call_pickup_and_user_associated(call_pickup, user1, user2):
    with a.call_pickup_interceptor_user(call_pickup, user1, user2, check=False):
        confd.callpickups(call_pickup['id']).delete().assert_deleted()

        deleted_call_pickup = confd.callpickups(call_pickup['id']).get
        yield s.check_resource_not_found, deleted_call_pickup, 'CallPickup'

        # When the relation will be added,
        # we should check if users have the key.callpickups to empty


@fixtures.call_pickup()
@fixtures.user()
def test_bus_events(call_pickup, user):
    url = confd.callpickups(call_pickup['id']).interceptors.users.put
    body = {'users': [user]}
    yield s.check_bus_event, 'config.callpickups.interceptors.users.updated', url, body
