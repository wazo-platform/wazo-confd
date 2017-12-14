# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from . import confd


def test_put_errors():
    url = confd.asterisk.iax.callnumberlimits.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'items', 123
    yield s.check_bogus_field_returns_error, url, 'items', None
    yield s.check_bogus_field_returns_error, url, 'items', {}
    yield s.check_bogus_field_returns_error, url, 'items', 'string'
    yield s.check_bogus_field_returns_error, url, 'items', ['string']
    yield s.check_bogus_field_returns_error, url, 'items', [{'key': 'value'}]

    regex = r'items.*ip_address'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'ip_address': 123}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'ip_address': True}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'ip_address': None}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'ip_address': {}}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'ip_address': []}], regex
    regex = r'items.*netmask'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'netmask': 123}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'netmask': True}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'netmask': None}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'netmask': {}}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'netmask': []}], regex
    regex = r'items.*limit'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'limit': 'string'}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'limit': None}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'limit': {}}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'limit': []}], regex


def test_get():
    response = confd.asterisk.iax.callnumberlimits.get()
    response.assert_ok()


def test_edit_iax_callnumberlimits():
    parameters = {'items': [{'ip_address': '127.0.0.1',
                             'netmask': '255.255.255.255',
                             'limit': 5}]}

    response = confd.asterisk.iax.callnumberlimits.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.iax.callnumberlimits.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_iax_callnumberlimits_without_items():
    parameters = {'items': []}
    response = confd.asterisk.iax.callnumberlimits.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.iax.callnumberlimits.get()
    assert_that(response.item, has_entries(parameters))


def test_bus_event_when_edited():
    url = confd.asterisk.iax.callnumberlimits
    yield s.check_bus_event, 'config.iax_callnumberlimits.edited', url.put, {'items': []}
