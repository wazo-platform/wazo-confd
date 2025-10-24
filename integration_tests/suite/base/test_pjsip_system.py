# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from ..helpers.config import TOKEN_SUB_TENANT
from . import confd


def test_put_errors():
    url = confd.asterisk.pjsip.system
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'options', 123)
    s.check_bogus_field_returns_error(url, 'options', None)
    s.check_bogus_field_returns_error(url, 'options', 'string')
    s.check_bogus_field_returns_error(url, 'options', [['ordered', 'option']])
    s.check_bogus_field_returns_error(url, 'options', {'wrong_value': 23})
    s.check_bogus_field_returns_error(url, 'options', {'none_value': None})
    # Not a system option
    s.check_bogus_field_returns_error(url, 'options', {'user_agent': 'yes'})
    # Should not be modified
    s.check_bogus_field_returns_error(url, 'options', {'type': 'endpoint'})


def test_get():
    response = confd.asterisk.pjsip.system.get()
    response.assert_ok()


def test_edit():
    parameters = {'options': {'compact_headers': 'yes', 'timer_b': '33500'}}

    response = confd.asterisk.pjsip.system.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.pjsip.system.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_with_no_option():
    parameters = {'options': {}}
    response = confd.asterisk.pjsip.system.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.pjsip.system.get()
    assert_that(response.item, has_entries(parameters))


def test_restrict_only_master_tenant():
    response = confd.asterisk.pjsip.system.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.asterisk.pjsip.system.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)


def test_bus_event_when_edited():
    url = confd.asterisk.pjsip.system
    headers = {}

    s.check_event('pjsip_system_updated', headers, url.put, {'options': {}})
