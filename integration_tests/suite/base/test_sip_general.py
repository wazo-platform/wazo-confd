# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from ..test_api import scenarios as s

from hamcrest import assert_that, has_entries
from . import confd


def test_put_errors():
    url = confd.asterisk.sip.general.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'ordered_options', 123
    yield s.check_bogus_field_returns_error, url, 'ordered_options', None
    yield s.check_bogus_field_returns_error, url, 'ordered_options', {}
    yield s.check_bogus_field_returns_error, url, 'ordered_options', 'string'
    yield s.check_bogus_field_returns_error, url, 'ordered_options', ['string', 'string']
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [123, 123]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', ['string', 123]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [[]]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [{'key': 'value'}]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [['missing_value']]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [['too', 'much', 'value']]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [['wrong_value', 1234]]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [['none_value', None]]

    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [['ordered', 'option']]
    yield s.check_bogus_field_returns_error, url, 'options', {'wrong_value': 23}
    yield s.check_bogus_field_returns_error, url, 'options', {'none_value': None}

    yield s.check_bogus_field_returns_error, url, 'options', {'register': 'value'}
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [['register', 'value']]


def test_get():
    response = confd.asterisk.sip.general.get()
    response.assert_ok()


def test_edit_sip_general():
    parameters = {'ordered_options': [['bindport', '5060'],
                                      ['allow', '127.0.0.1'],
                                      ['deny', '192.168.0.0'],
                                      ['allow', '192.168.0.1']],
                  'options': {'nat': 'toto',
                              'username': 'Bob'}}

    response = confd.asterisk.sip.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.sip.general.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_sip_general_with_no_option():
    parameters = {'ordered_options': [],
                  'options': {}}
    response = confd.asterisk.sip.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.sip.general.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_sip_general_with_none_value():
    parameters = {'ordered_options': [['bindport', 'ip']],
                  'options': {'nat': 'value'}}

    response = confd.asterisk.sip.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.sip.general.get()
    assert_that(response.item, has_entries(parameters))


def test_bus_event_when_edited():
    url = confd.asterisk.sip.general
    yield s.check_bus_event, 'config.sip_general.edited', url.put, {'ordered_options': [], 'options': {}}
