# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from ..helpers import scenarios as s

from hamcrest import assert_that, has_entries
from . import confd


def test_put_errors():
    url = confd.asterisk.voicemail.zonemessages.put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'items', 123
    yield s.check_bogus_field_returns_error, url, 'items', None
    yield s.check_bogus_field_returns_error, url, 'items', {}
    yield s.check_bogus_field_returns_error, url, 'items', 'string'
    yield s.check_bogus_field_returns_error, url, 'items', ['string']
    yield s.check_bogus_field_returns_error, url, 'items', [{'key': 'value'}]

    regex = r'items.*name'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'name': 123}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'name': True}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'name': None}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'name': {}}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'name': []}], regex
    regex = r'items.*timezone'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'timezone': 123}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'timezone': True}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'timezone': None}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'timezone': {}}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'timezone': []}], regex

    regex = r'items.*message'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'message': 123}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'message': True}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'message': {}}], regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'items', [{'message': []}], regex


def test_get():
    response = confd.asterisk.voicemail.zonemessages.get()
    response.assert_ok()


def test_edit_voicemail_zonemessages():
    parameters = {'items': [{'name': 'ny',
                             'timezone': 'America/New_York',
                             'message': "'vm-received' Q 'digits/at' IMp"}]}

    response = confd.asterisk.voicemail.zonemessages.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.voicemail.zonemessages.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_voicemail_zonemessages_without_items():
    parameters = {'items': []}
    response = confd.asterisk.voicemail.zonemessages.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.voicemail.zonemessages.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_voicemail_zonemessages_with_none_message():
    parameters = {'items': [{'name': 'ny',
                             'timezone': 'America/New_York',
                             'message': None}]}

    response = confd.asterisk.voicemail.zonemessages.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.voicemail.zonemessages.get()
    assert_that(response.item, has_entries(parameters))


def test_bus_event_when_edited():
    url = confd.asterisk.voicemail.zonemessages
    yield s.check_bus_event, 'config.voicemail_zonemessages.edited', url.put, {'items': []}
