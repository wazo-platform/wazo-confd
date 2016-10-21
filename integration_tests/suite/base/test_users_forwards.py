# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import unicode_literals
from hamcrest import assert_that, has_key, has_entries, equal_to

from test_api import confd
from test_api import fixtures
from test_api import scenarios as s

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
    yield s.check_bogus_field_returns_error, forward_url, 'destination', {}


@fixtures.user()
def test_get_forwards_relation(user):
    forwards = {'busy': {'enabled': True, 'destination': '123'},
                'noanswer': {'enabled': True, 'destination': '456'},
                'unconditional': {'enabled': True, 'destination': '789'}}
    confd.users(user['uuid']).forwards.put(**forwards).assert_updated()

    response = confd.users(user['uuid']).get()
    assert_that(response.item, has_entries(forwards=forwards))
