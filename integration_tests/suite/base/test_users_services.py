# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, equal_to, has_entries, has_entry, has_key

from ..helpers import fixtures
from ..helpers import scenarios as s
from . import confd

VALID_SERVICES = ['dnd', 'incallfilter']


@fixtures.user()
def test_get_users_services(user):
    response = confd.users(user['uuid']).services.get()
    for service in VALID_SERVICES:
        assert_that(response.item, has_key(service))


@fixtures.user()
def test_get_value_for_each_user_service(user):
    for service in VALID_SERVICES:
        service_url = confd.users(user['uuid']).services(service)
        _read_service(service_url, False)


@fixtures.user()
def test_put_value_for_each_user_service(user):
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


@fixtures.user()
def test_put_services(user):
    services_url = confd.users(user['uuid']).services
    _update_services(services_url, {'enabled': True}, {'enabled': False})


def _update_services(services_url, dnd={}, incallfilter={}):
    response = services_url.put(dnd=dnd, incallfilter=incallfilter)
    response.assert_ok()

    response = services_url.get()
    assert_that(response.item, equal_to({'dnd': dnd, 'incallfilter': incallfilter}))


@fixtures.user()
def test_put_error(user):
    service_url = confd.users(user['uuid']).services('dnd').put
    s.check_bogus_field_returns_error(service_url, 'enabled', 'string')
    s.check_bogus_field_returns_error(service_url, 'enabled', None)
    s.check_bogus_field_returns_error(service_url, 'enabled', 123)
    s.check_bogus_field_returns_error(service_url, 'enabled', [])
    s.check_bogus_field_returns_error(service_url, 'enabled', {})


@fixtures.user(services={'dnd': {'enabled': True}, 'incallfilter': {'enabled': True}})
def test_get_services_relation(user):
    response = confd.users(user['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            services={'dnd': {'enabled': True}, 'incallfilter': {'enabled': True}}
        ),
    )
