# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from . import confd
from ..helpers import scenarios as s
from ..helpers.config import TOKEN_SUB_TENANT


def test_put_errors():
    url = confd.asterisk.confbridge.wazo_default_user.put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'options', 123)
    s.check_bogus_field_returns_error(url, 'options', None)
    s.check_bogus_field_returns_error(url, 'options', 'string')
    s.check_bogus_field_returns_error(url, 'options', [['ordered', 'option']])
    s.check_bogus_field_returns_error(url, 'options', {'wrong_value': 23})
    s.check_bogus_field_returns_error(url, 'options', {'none_value': None})


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


def test_restrict_only_master_tenant():
    response = confd.asterisk.confbridge.wazo_default_user.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.asterisk.confbridge.wazo_default_user.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)


def test_bus_event_when_edited():
    url = confd.asterisk.confbridge.wazo_default_user
    headers = {}

    s.check_event(
        'confbridge_wazo_default_user_edited', headers, url.put, {'options': {}}
    )
