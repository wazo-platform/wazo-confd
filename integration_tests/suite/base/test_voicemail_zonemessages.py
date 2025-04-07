# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from ..helpers.config import TOKEN_SUB_TENANT
from . import confd


def test_put_errors():
    url = confd.asterisk.voicemail.zonemessages.put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'items', 123)
    s.check_bogus_field_returns_error(url, 'items', None)
    s.check_bogus_field_returns_error(url, 'items', {})
    s.check_bogus_field_returns_error(url, 'items', 'string')
    s.check_bogus_field_returns_error(url, 'items', ['string'])
    s.check_bogus_field_returns_error(url, 'items', [{'key': 'value'}])

    regex = r'items.*name'
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'name': 123}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'name': True}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'name': None}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'name': {}}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'name': []}], regex
    )
    regex = r'items.*timezone'
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'timezone': 123}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'timezone': True}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'timezone': None}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'timezone': {}}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'timezone': []}], regex
    )

    regex = r'items.*message'
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'message': 123}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'message': True}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'message': {}}], regex
    )
    s.check_bogus_field_returns_error_matching_regex(
        url, 'items', [{'message': []}], regex
    )


def test_get():
    response = confd.asterisk.voicemail.zonemessages.get()
    response.assert_ok()


def test_edit_voicemail_zonemessages():
    parameters = {
        'items': [
            {
                'name': 'ny',
                'timezone': 'America/New_York',
                'message': "'vm-received' Q 'digits/at' IMp",
            }
        ]
    }

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
    parameters = {
        'items': [{'name': 'ny', 'timezone': 'America/New_York', 'message': None}]
    }

    response = confd.asterisk.voicemail.zonemessages.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.voicemail.zonemessages.get()
    assert_that(response.item, has_entries(parameters))


def test_restrict_only_master_tenant():
    response = confd.asterisk.voicemail.zonemessages.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)


def test_that_list_is_not_restricted_to_the_master_tenant():
    response = confd.asterisk.voicemail.zonemessages.get(token=TOKEN_SUB_TENANT)
    response.assert_status(200)


def test_bus_event_when_edited():
    url = confd.asterisk.voicemail.zonemessages
    headers = {}

    s.check_event('voicemail_zonemessages_edited', headers, url.put, {'items': []})
