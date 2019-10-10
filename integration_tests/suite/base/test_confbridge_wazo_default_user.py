# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from . import confd
from ..helpers import scenarios as s


def test_put_errors():
    url = confd.asterisk.confbridge.wazo_default_user.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [['ordered', 'option']]
    yield s.check_bogus_field_returns_error, url, 'options', {'wrong_value': 23}
    yield s.check_bogus_field_returns_error, url, 'options', {'none_value': None}


def test_get():
    response = confd.asterisk.confbridge.wazo_default_user.get()
    response.assert_ok()


def test_edit_confbridge_wazo_default_user():
    parameters = {'options': {'nat': 'toto', 'username': 'Bob'}}

    response = confd.asterisk.confbridge.wazo_default_user.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.confbridge.wazo_default_user.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_confbridge_wazo_default_user_with_no_option():
    parameters = {'options': {}}
    response = confd.asterisk.confbridge.wazo_default_user.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.confbridge.wazo_default_user.get()
    assert_that(response.item, has_entries(parameters))


def test_bus_event_when_edited():
    url = confd.asterisk.confbridge.wazo_default_user
    yield s.check_bus_event, 'config.confbridge_wazo_default_user.edited', url.put, {
        'options': {}
    }
