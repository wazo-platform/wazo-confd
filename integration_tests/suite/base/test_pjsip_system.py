# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from . import confd
from ..helpers import scenarios as s


def test_put_errors():
    url = confd.asterisk.pjsip.system.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [['ordered', 'option']]
    yield s.check_bogus_field_returns_error, url, 'options', {'wrong_value': 23}
    yield s.check_bogus_field_returns_error, url, 'options', {'none_value': None}
    # Not a system option
    yield s.check_bogus_field_returns_error, url, 'options', {'user_agent': 'yes'}
    # Should not be modified
    yield s.check_bogus_field_returns_error, url, 'options', {'type': 'endpoint'}


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


def test_bus_event_when_edited():
    url = confd.asterisk.pjsip.system
    yield s.check_bus_event, 'config.pjsip_system.updated', url.put, {'options': {}}
