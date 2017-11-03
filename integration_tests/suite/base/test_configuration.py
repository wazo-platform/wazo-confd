# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from hamcrest import assert_that

from test_api import scenarios as s
from . import confd


def test_put_errors():
    url = confd.configuration.live_reload.put

    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'enabled', 1
    yield s.check_bogus_field_returns_error, url, 'enabled', None
    yield s.check_bogus_field_returns_error, url, 'enabled', 'string'
    yield s.check_bogus_field_returns_error, url, 'enabled', []
    yield s.check_bogus_field_returns_error, url, 'enabled', {}


def test_live_reload_true():
    expected = {'enabled': True}
    response = confd.configuration.live_reload.put(expected)
    response.assert_updated()

    response = confd.configuration.live_reload.get()
    assert_that(response.item, expected)


def test_live_reload_false():
    expected = {'enabled': False}
    response = confd.configuration.live_reload.put(expected)
    response.assert_updated()

    response = confd.configuration.live_reload.get()
    assert_that(response.item, expected)
