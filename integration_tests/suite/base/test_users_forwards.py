# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals
from hamcrest import assert_that, has_key, has_entries, equal_to

from . import confd
from ..helpers import fixtures
from ..helpers import scenarios as s

VALID_FORWARDS = ['busy',
                  'noanswer',
                  'unconditional']


@fixtures.user()
def test_get_users_forwards(user):
    response = confd.users(user['uuid']).forwards.get()
    for forward in VALID_FORWARDS:
        assert_that(response.item, has_key(forward))


@fixtures.user()
def test_get_for_each_user_forward(user):
    for forward in VALID_FORWARDS:
        forward_url = confd.users(user['uuid']).forwards(forward)
        yield _read_forward, forward_url, False


@fixtures.user()
def test_put_for_each_user_forward(user):
    for forward in VALID_FORWARDS:
        forward_url = confd.users(user['uuid']).forwards(forward)
        yield _update_forward, forward_url, False
        yield _update_forward, forward_url, True, '123'


def _update_forward(forward_url, enabled, destination=None):
    response = forward_url.put(enabled=enabled, destination=destination)
    response.assert_ok()
    _read_forward(forward_url, enabled=enabled, destination=destination)


def _read_forward(forward_url, enabled, destination=None):
    response = forward_url.get()
    assert_that(response.item, has_entries({'enabled': enabled, 'destination': destination}))


@fixtures.user()
def test_put_forwards(user):
    forwards_url = confd.users(user['uuid']).forwards
    yield _update_forwards, forwards_url, {'enabled': True, 'destination': '123'}, \
                                          {'enabled': False, 'destination': '456'}, \
                                          {'enabled': False, 'destination': None}


def _update_forwards(forwards_url, busy={}, noanswer={}, unconditional={}):
    response = forwards_url.put(busy=busy, noanswer=noanswer, unconditional=unconditional)
    response.assert_ok()

    response = forwards_url.get()
    assert_that(response.item, equal_to({'busy': busy, 'noanswer': noanswer, 'unconditional': unconditional}))


@fixtures.user()
def test_error_on_null_destination_when_enabled(user):
    for forward in VALID_FORWARDS:
        response = confd.users(user['uuid']).forwards(forward).put(enabled=True, destination=None)
        response.assert_status(400)


@fixtures.user()
def test_put_error(user):
    forward_url = confd.users(user['uuid']).forwards('busy').put
    yield s.check_bogus_field_returns_error, forward_url, 'enabled', 'string'
    yield s.check_bogus_field_returns_error, forward_url, 'enabled', None
    yield s.check_bogus_field_returns_error, forward_url, 'enabled', 123
    yield s.check_bogus_field_returns_error, forward_url, 'enabled', 1
    yield s.check_bogus_field_returns_error, forward_url, 'enabled', 0
    yield s.check_bogus_field_returns_error, forward_url, 'enabled', {}
    yield s.check_bogus_field_returns_error, forward_url, 'destination', True
    yield s.check_bogus_field_returns_error, forward_url, 'destination', 123
    yield s.check_bogus_field_returns_error, forward_url, 'destination', s.random_string(129)
    yield s.check_bogus_field_returns_error, forward_url, 'destination', {}


@fixtures.user(forwards={'busy': {'enabled': True, 'destination': '123'},
                         'noanswer': {'enabled': True, 'destination': '456'},
                         'unconditional': {'enabled': True, 'destination': '789'}})
def test_get_forwards_relation(user):
    response = confd.users(user['uuid']).get()
    assert_that(response.item, has_entries(
        forwards={'busy': {'enabled': True, 'destination': '123'},
                  'noanswer': {'enabled': True, 'destination': '456'},
                  'unconditional': {'enabled': True, 'destination': '789'}}
    ))
