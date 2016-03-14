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
from hamcrest import assert_that, has_key, has_entry

from test_api import confd
from test_api import fixtures
from test_api import scenarios as s

VALID_SERVICES = ['dnd',
                  'incallfilter']


@fixtures.user()
def test_get_users_services(user):
    response = confd.users(user['uuid']).services.get()
    for service in VALID_SERVICES:
        assert_that(response.item, has_key(service))


@fixtures.user()
def test_get_value_for_each_user_service(user):
    for service in VALID_SERVICES:
        service_url = confd.users(user['uuid']).services(service)
        yield _read_service, service_url, False


@fixtures.user()
def test_put_value_for_each_user_service(user):
    for service in VALID_SERVICES:
        service_url = confd.users(user['uuid']).services(service)
        yield _update_service, service_url, False
        yield _update_service, service_url, True


def _update_service(service_url, value):
    response = service_url.put(enabled=value)
    response.assert_ok()
    _read_service(service_url, value)


def _read_service(service_url, value):
    response = service_url.get()
    assert_that(response.item, has_entry('enabled', value))


@fixtures.user()
def test_error_on_wrong_service(user):
    service_url = confd.users(user['uuid']).services('toto')
    yield s.check_resource_not_found, service_url.get, 'Service'


@fixtures.user()
def test_put_error(user):
    service_url = confd.users(user['uuid']).services('dnd').put
    yield s.check_bogus_field_returns_error, service_url, 'enabled', 'string'
    yield s.check_bogus_field_returns_error, service_url, 'enabled', None
    yield s.check_bogus_field_returns_error, service_url, 'enabled', 123
    yield s.check_bogus_field_returns_error, service_url, 'enabled', []
    yield s.check_bogus_field_returns_error, service_url, 'enabled', {}
