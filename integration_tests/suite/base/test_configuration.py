# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that

from . import confd
from ..helpers import scenarios as s
from ..helpers.config import TOKEN_SUB_TENANT


def test_put_errors():
    url = confd.configuration.live_reload.put

    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'enabled', 1)
    s.check_bogus_field_returns_error(url, 'enabled', None)
    s.check_bogus_field_returns_error(url, 'enabled', 'string')
    s.check_bogus_field_returns_error(url, 'enabled', [])
    s.check_bogus_field_returns_error(url, 'enabled', {})


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


def test_restrict_only_master_tenant():
    response = confd.configuration.live_reload.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.configuration.live_reload.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)
