# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from uuid import uuid4

from hamcrest import assert_that, has_entries, has_entry, has_item, is_not

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import TOKEN_SUB_TENANT
from . import confd

FAKE_UUID = uuid4()


def test_search_errors():
    url = confd.extensions.features.get
    s.search_error_checks(url)


def test_get_errors():
    url = confd.extensions.features(FAKE_UUID).get
    s.check_resource_not_found(url, 'FeatureExtension')


@fixtures.extension_feature()
def test_put_errors(extension):
    url = confd.extensions.features(FAKE_UUID).put
    s.check_resource_not_found(url, 'FeatureExtension')

    url = confd.extensions.features(extension['uuid'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


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


@fixtures.extension_feature()
def test_delete_unimplemented(extension):
    response = confd.extensions.features(extension['uuid']).delete()
    response.assert_status(405)


@fixtures.extension_feature(exten='4999', feature='search')
@fixtures.extension_feature(exten='9999', feature='hidden')
def test_search(extension, hidden):
    url = confd.extensions.features
    searches = {'exten': '499', 'feature': 'sea'}

    for field, term in searches.items():
        check_search(url, extension, hidden, field, term)


def check_search(url, extension, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, extension[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: extension[field]})
    assert_that(response.items, has_item(has_entry('uuid', extension['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


@fixtures.extension_feature(exten='9998')
@fixtures.extension_feature(exten='9999')
def test_sorting_offset_limit(extension1, extension2):
    url = confd.extensions.features.get
    id_field = 'uuid'
    s.check_sorting(url, extension1, extension2, 'exten', '999', id_field)

    s.check_offset(url, extension1, extension2, 'exten', '999', id_field)
    s.check_limit(url, extension1, extension2, 'exten', '999', id_field)


@fixtures.extension_feature()
def test_get(extension):
    response = confd.extensions.features(extension['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            exten=extension['exten'],
            feature=extension['feature'],
            enabled=True,
        ),
    )


@fixtures.extension_feature()
def test_edit_minimal_parameters(extension):
    response = confd.extensions.features(extension['uuid']).put()
    response.assert_updated()


@fixtures.extension_feature()
def test_edit_all_parameters(extension):
    parameters = {'exten': '*911', 'enabled': False}

    response = confd.extensions.features(extension['uuid']).put(**parameters)
    response.assert_updated()

    response = confd.extensions.features(extension['uuid']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.extension_feature(exten='1234')
@fixtures.extension_feature()
def test_edit_with_same_extension(extension1, extension2):
    response = confd.extensions.features(extension2['uuid']).put(
        exten=extension1['exten']
    )
    response.assert_match(400, e.resource_exists('FeatureExtension'))


@fixtures.extension_feature()
def test_restrict_only_master_tenant(extension):
    response = confd.extensions.features.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.extensions.features(extension['uuid']).put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.extensions.features(extension['uuid']).get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)


@fixtures.extension_feature()
def test_bus_events(extension):
    headers = {}
    s.check_event(
        'extension_feature_edited',
        headers,
        confd.extensions.features(extension['uuid']).put,
    )
