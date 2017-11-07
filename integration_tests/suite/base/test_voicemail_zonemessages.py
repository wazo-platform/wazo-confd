# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from test_api import scenarios as s

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
