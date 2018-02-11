# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
)

from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s
)
from . import confd

FAKE_ID = 999999999


def test_search_errors():
    url = confd.extensions.features.get
    for check in s.search_error_checks(url):
        yield check


def test_get_errors():
    url = confd.extensions.features(FAKE_ID).get
    yield s.check_resource_not_found, url, 'Extension'


@fixtures.extension_feature()
def test_put_errors(extension):
    url = confd.extensions.features(FAKE_ID).put
    yield s.check_resource_not_found, url, 'Extension'

    url = confd.extensions.features(extension['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'exten', None
    yield s.check_bogus_field_returns_error, url, 'exten', True
    yield s.check_bogus_field_returns_error, url, 'exten', 'ABC123'
    yield s.check_bogus_field_returns_error, url, 'exten', 'XXXX'
    yield s.check_bogus_field_returns_error, url, 'exten', {}
    yield s.check_bogus_field_returns_error, url, 'exten', []
    yield s.check_bogus_field_returns_error, url, 'enabled', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'enabled', None
    yield s.check_bogus_field_returns_error, url, 'enabled', []
    yield s.check_bogus_field_returns_error, url, 'enabled', {}


def test_put_bulk_errors():
    url = confd.extensions.features.put

    regex = r'features.*exten'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'features', {'exten': None}, regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'features', {'exten': True}, regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'features', {'exten': 'ABC123'}, regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'features', {'exten': 'XXXX'}, regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'features', {'exten': {}}, regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'features', {'exten': []}, regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'features', {'exten': []}, regex

    regex = r'features.*enabled'
    yield s.check_bogus_field_returns_error_matching_regex, url, 'features', {'enabled', 'invalid'}, regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'features', {'enabled', None}, regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'features', {'enabled', []}, regex
    yield s.check_bogus_field_returns_error_matching_regex, url, 'features', {'enabled', {}}, regex


def test_create_unimplemented():
    response = confd.extensions.features.post()
    response.assert_status(405)


@fixtures.extension_feature()
def test_delete_unimplemented(extension):
    response = confd.extensions.features(extension['id']).delete()
    response.assert_status(405)


@fixtures.extension_feature(exten='4999')
@fixtures.extension_feature(exten='9999')
def test_search(extension, hidden):
    url = confd.extensions.features
    searches = {'exten': '499'}

    for field, term in searches.items():
        yield check_search, url, extension, hidden, field, term


def check_search(url, extension, hidden, field, term):
    response = url.get(search=term)

    expected_extension = has_item(has_entry(field, extension[field]))
    hidden_extension = is_not(has_item(has_entry(field, hidden[field])))
    assert_that(response.items, expected_extension)
    assert_that(response.items, hidden_extension)

    response = url.get(**{field: extension[field]})

    expected_extension = has_item(has_entry('id', extension['id']))
    hidden_extension = is_not(has_item(has_entry('id', hidden['id'])))
    assert_that(response.items, expected_extension)
    assert_that(response.items, hidden_extension)


@fixtures.extension_feature(exten='9998')
@fixtures.extension_feature(exten='9999')
def test_sorting_offset_limit(extension1, extension2):
    url = confd.extensions.features.get
    yield s.check_sorting, url, extension1, extension2, 'exten', '999'

    yield s.check_offset, url, extension1, extension2, 'exten', '999'
    yield s.check_offset_legacy, url, extension1, extension2, 'exten', '999'

    yield s.check_limit, url, extension1, extension2, 'exten', '999'


@fixtures.extension_feature()
def test_get(extension):
    response = confd.extensions.features(extension['id']).get()
    assert_that(response.item, has_entries(
        exten=extension['exten'],
        context=extension['context'],
        feature=extension['feature'],
        enabled=True,
    ))


@fixtures.extension_feature()
def test_edit_minimal_parameters(extension):
    response = confd.extensions.features(extension['id']).put()
    response.assert_updated()


@fixtures.extension_feature()
def test_edit_all_parameters(extension):
    parameters = {'exten': '*911',
                  'enabled': False}

    response = confd.extensions.features(extension['id']).put(**parameters)
    response.assert_updated()

    response = confd.extensions.features(extension['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.extension_feature(exten='1234')
@fixtures.extension_feature()
def test_edit_with_same_extension(extension1, extension2):
    response = confd.extensions.features(extension2['id']).put(exten=extension1['exten'])
    response.assert_match(400, e.resource_exists('Extension'))


@fixtures.extension_feature()
def test_edit_bulk_do_nothing(_):
    parameters = {'features': []}

    response = confd.extensions.features.put(**parameters)
    response.assert_updated()

    response = confd.extensions.features.get()
    assert_that(response.item, is_not(empty()))


@fixtures.extension_feature()
@fixtures.extension_feature()
def test_edit_bulk_swap(extension1, extension2):
    parameters = {'features': [
        {'id': extension1['id'],
         'exten': extension2['exten'],
         'enabled': False},
        {'id': extension2['id'],
         'exten': extension1['exten'],
         'enabled': True},
    ]}

    response = confd.extensions.features.put(**parameters)
    response.assert_updated()

    response = confd.extensions.features.get()
    assert_that(response.item, has_items(
        has_entry(
            id=extension1['id'],
            extension=extension2['exten'],
            enabled=False
        ),
        has_entry(
            id=extension2['id'],
            extension=extension1['exten'],
            enabled=False
        ),
    ))


@fixtures.extension_feature()
def test_edit_bulk_with_same_extension(extension):
    # TODO
    pass


@fixtures.extension_feature()
@fixtures.extension_feature()
def test_edit_bulk_with_existing_extension(extension1, extension2):
    parameters = {'features': [
        {'id': extension2['id'],
         'exten': extension1['exten']}
    ]}

    response = confd.extensions.features.put(**parameters)
    response.assert_match(400, e.resource_exists('Extension'))


@fixtures.extension_feature()
def test_bus_events(extension):
    yield s.check_bus_event, 'config.extension_feature.edited', confd.extensions.features(extension['id']).put
