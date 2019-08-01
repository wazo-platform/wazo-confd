# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    equal_to,
    has_key,
    has_entry,
    has_entries,
)

from . import confd
from ..helpers import fixtures
from ..helpers import scenarios as s

VALID_SERVICES = ['dnd',
                  'incallfilter']


def test_get_users_services():
    with fixtures.user() as user:
        response = confd.users(user['uuid']).services.get()
        for service in VALID_SERVICES:
            assert_that(response.item, has_key(service))



def test_get_value_for_each_user_service():
    with fixtures.user() as user:
        for service in VALID_SERVICES:
            service_url = confd.users(user['uuid']).services(service)
            _read_service(service_url, False)


def test_put_value_for_each_user_service():
    with fixtures.user() as user:
        for service in VALID_SERVICES:
            service_url = confd.users(user['uuid']).services(service)
            _update_service(service_url, False)
            _update_service(service_url, True)


def _update_service(service_url, value):
    response = service_url.put(enabled=value)
    response.assert_ok()
    _read_service(service_url, value)


def _read_service(service_url, value):
    response = service_url.get()
    assert_that(response.item, has_entry('enabled', value))


def test_put_services():
    with fixtures.user() as user:
        services_url = confd.users(user['uuid']).services
        _update_services(services_url, {'enabled': True}, {'enabled': False})



def _update_services(services_url, dnd={}, incallfilter={}):
    response = services_url.put(dnd=dnd, incallfilter=incallfilter)
    response.assert_ok()

    response = services_url.get()
    assert_that(response.item, equal_to({'dnd': dnd, 'incallfilter': incallfilter}))


def test_put_error():
    with fixtures.user() as user:
        service_url = confd.users(user['uuid']).services('dnd').put
        s.check_bogus_field_returns_error(service_url, 'enabled', 'string')
        s.check_bogus_field_returns_error(service_url, 'enabled', None)
        s.check_bogus_field_returns_error(service_url, 'enabled', 123)
        s.check_bogus_field_returns_error(service_url, 'enabled', [])
        s.check_bogus_field_returns_error(service_url, 'enabled', {})



def test_get_services_relation():
    with fixtures.user(services={'dnd': {'enabled': True}, 'incallfilter': {'enabled': True}}) as user:
        response = confd.users(user['uuid']).get()
        assert_that(response.item, has_entries(
            services={'dnd': {'enabled': True},
                      'incallfilter': {'enabled': True}}
        ))

