# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
    has_entry,
    has_item,
    is_not,
)

from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)

FAKE_ID = 999999999


def test_search_errors():
    url = confd.extensions.features.get
    s.search_error_checks(url)


def test_get_errors():
    url = confd.extensions.features(FAKE_ID).get
    s.check_resource_not_found(url, 'Extension')


def test_put_errors():
    with fixtures.extension_feature() as extension:
        url = confd.extensions.features(FAKE_ID).put
        s.check_resource_not_found(url, 'Extension')

        url = confd.extensions.features(extension['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'exten', None)
    s.check_bogus_field_returns_error(url, 'exten', True)
    s.check_bogus_field_returns_error(url, 'exten', 'ABC123')
    s.check_bogus_field_returns_error(url, 'exten', 'XXXX')
    s.check_bogus_field_returns_error(url, 'exten', {})
    s.check_bogus_field_returns_error(url, 'exten', [])
    s.check_bogus_field_returns_error(url, 'enabled', 'invalid')
    s.check_bogus_field_returns_error(url, 'enabled', None)
    s.check_bogus_field_returns_error(url, 'enabled', [])
    s.check_bogus_field_returns_error(url, 'enabled', {})


def test_create_unimplemented():
    response = confd.extensions.features.post()
    response.assert_status(405)


def test_delete_unimplemented():
    with fixtures.extension_feature() as extension:
        response = confd.extensions.features(extension['id']).delete()
        response.assert_status(405)



def test_search():
    with fixtures.extension_feature(exten='4999', feature='search') as extension, fixtures.extension_feature(exten='9999', feature='hidden') as hidden:
        url = confd.extensions.features
        searches = {
            'exten': '499',
            'feature': 'sea',
        }

        for field, term in searches.items():
            check_search(url, extension, hidden, field, term)



def check_search(url, extension, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, extension[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: extension[field]})
    assert_that(response.items, has_item(has_entry('id', extension['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def test_sorting_offset_limit():
    with fixtures.extension_feature(exten='9998') as extension1, fixtures.extension_feature(exten='9999') as extension2:
        url = confd.extensions.features.get
        s.check_sorting(url, extension1, extension2, 'exten', '999')

        s.check_offset(url, extension1, extension2, 'exten', '999')
        s.check_offset_legacy(url, extension1, extension2, 'exten', '999')

        s.check_limit(url, extension1, extension2, 'exten', '999')



def test_get():
    with fixtures.extension_feature() as extension:
        response = confd.extensions.features(extension['id']).get()
        assert_that(response.item, has_entries(
            exten=extension['exten'],
            context=extension['context'],
            feature=extension['feature'],
            enabled=True,
        ))



def test_edit_minimal_parameters():
    with fixtures.extension_feature() as extension:
        response = confd.extensions.features(extension['id']).put()
        response.assert_updated()



def test_edit_all_parameters():
    with fixtures.extension_feature() as extension:
        parameters = {'exten': '*911', 'enabled': False}

        response = confd.extensions.features(extension['id']).put(**parameters)
        response.assert_updated()

        response = confd.extensions.features(extension['id']).get()
        assert_that(response.item, has_entries(parameters))



def test_edit_with_same_extension():
    with fixtures.extension_feature(exten='1234') as extension1, fixtures.extension_feature() as extension2:
        response = confd.extensions.features(extension2['id']).put(exten=extension1['exten'])
        response.assert_match(400, e.resource_exists('Extension'))



def test_bus_events():
    with fixtures.extension_feature() as extension:
        s.check_bus_event('config.extension_feature.edited', confd.extensions.features(extension['id']).put)

