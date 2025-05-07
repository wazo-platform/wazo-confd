# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to, has_entries, has_key

from ..helpers import fixtures
from ..helpers import scenarios as s
from . import confd

VALID_FORWARDS = ['busy', 'noanswer', 'unconditional']


@fixtures.user()
def test_get_users_forwards(user):
    response = confd.users(user['uuid']).forwards.get()
    for forward in VALID_FORWARDS:
        assert_that(response.item, has_key(forward))


@fixtures.user()
def test_get_for_each_user_forward(user):
    for forward in VALID_FORWARDS:
        forward_url = confd.users(user['uuid']).forwards(forward)
        _read_forward(forward_url, False)


@fixtures.user()
def test_put_for_each_user_forward(user):
    for forward in VALID_FORWARDS:
        forward_url = confd.users(user['uuid']).forwards(forward)
        _update_forward(forward_url, False)
        _update_forward(forward_url, True, '123')


def _update_forward(forward_url, enabled, destination=None):
    response = forward_url.put(enabled=enabled, destination=destination)
    response.assert_ok()
    _read_forward(forward_url, enabled=enabled, destination=destination)


def _read_forward(forward_url, enabled, destination=None):
    response = forward_url.get()
    assert_that(
        response.item, has_entries({'enabled': enabled, 'destination': destination})
    )


@fixtures.user()
def test_put_forwards(user):
    forwards_url = confd.users(user['uuid']).forwards
    _update_forwards(
        forwards_url,
        {'enabled': True, 'destination': '123'},
        {
            'enabled': False,
            'destination': '456',
        },
        {'enabled': False, 'destination': None},
    )


def _update_forwards(forwards_url, busy={}, noanswer={}, unconditional={}):
    response = forwards_url.put(
        busy=busy, noanswer=noanswer, unconditional=unconditional
    )
    response.assert_ok()

    response = forwards_url.get()
    assert_that(
        response.item,
        equal_to({'busy': busy, 'noanswer': noanswer, 'unconditional': unconditional}),
    )


@fixtures.user()
def test_error_on_null_destination_when_enabled(user):
    for forward in VALID_FORWARDS:
        response = (
            confd.users(user['uuid'])
            .forwards(forward)
            .put(enabled=True, destination=None)
        )
        response.assert_status(400)


@fixtures.user()
def test_put_error(user):
    forward_url = confd.users(user['uuid']).forwards('busy').put
    s.check_bogus_field_returns_error(forward_url, 'enabled', 'string')
    s.check_bogus_field_returns_error(forward_url, 'enabled', None)
    s.check_bogus_field_returns_error(forward_url, 'enabled', 123)
    s.check_bogus_field_returns_error(forward_url, 'enabled', 1)
    s.check_bogus_field_returns_error(forward_url, 'enabled', 0)
    s.check_bogus_field_returns_error(forward_url, 'enabled', {})
    s.check_bogus_field_returns_error(forward_url, 'destination', True)
    s.check_bogus_field_returns_error(forward_url, 'destination', 123)
    s.check_bogus_field_returns_error(forward_url, 'destination', s.random_string(129))
    s.check_bogus_field_returns_error(forward_url, 'destination', {})


@fixtures.user(
    forwards={
        'busy': {'enabled': True, 'destination': '123'},
        'noanswer': {'enabled': True, 'destination': '456'},
        'unconditional': {'enabled': True, 'destination': '789'},
    }
)
def test_get_forwards_relation(user):
    response = confd.users(user['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            forwards={
                'busy': {'enabled': True, 'destination': '123'},
                'noanswer': {'enabled': True, 'destination': '456'},
                'unconditional': {'enabled': True, 'destination': '789'},
            }
        ),
    )
