# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that

from . import confd
from ..helpers import scenarios as s


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
