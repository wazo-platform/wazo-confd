# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from . import confd


def test_put_errors():
    url = confd.asterisk.iax.callnumberlimits.put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'items', 123)
    s.check_bogus_field_returns_error(url, 'items', None)
    s.check_bogus_field_returns_error(url, 'items', {})
    s.check_bogus_field_returns_error(url, 'items', 'string')
    s.check_bogus_field_returns_error(url, 'items', ['string'])
    s.check_bogus_field_returns_error(url, 'items', [{'key': 'value'}])

    regex = r'items.*ip_address'
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'ip_address': 123}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'ip_address': True}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'ip_address': None}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'ip_address': {}}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'ip_address': []}], regex)
    regex = r'items.*netmask'
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'netmask': 123}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'netmask': True}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'netmask': None}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'netmask': {}}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'netmask': []}], regex)
    regex = r'items.*limit'
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'limit': 'string'}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'limit': None}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'limit': {}}], regex)
    s.check_bogus_field_returns_error_matching_regex(url, 'items', [{'limit': []}], regex)


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
    s.check_bus_event('config.iax_callnumberlimits.edited', url.put, {'items': []})
