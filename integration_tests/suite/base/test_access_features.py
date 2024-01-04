# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, empty, has_entries, has_entry, has_item, is_not, not_

from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import TOKEN_SUB_TENANT


def test_get_errors():
    fake_access_feature = confd.access_features(999999).get
    s.check_resource_not_found(fake_access_feature, 'AccessFeatures')


def test_delete_errors():
    fake_access_feature = confd.access_features(999999).delete
    s.check_resource_not_found(fake_access_feature, 'AccessFeatures')


def test_post_errors():
    url = confd.access_features.post
    error_checks(url)


@fixtures.access_feature()
def test_put_errors(access_feature):
    url = confd.access_features(access_feature['id']).put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'host', None)
    s.check_bogus_field_returns_error(url, 'enabled', 'invalid')
    s.check_bogus_field_returns_error(url, 'enabled', None)
    s.check_bogus_field_returns_error(url, 'feature', 'invalid')
    s.check_bogus_field_returns_error(url, 'feature', None)


@fixtures.access_feature(host='1.2.3.0/24', enabled=False)
@fixtures.access_feature(host='1.2.4.0/24')
def test_search(access_feature, hidden):
    url = confd.access_features
    searches = {'host': '1.2.3', 'enabled': False}

    for field, term in searches.items():
        check_search(url, access_feature, hidden, field, term)


def check_search(url, context, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, context[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: context[field]})
    assert_that(response.items, has_item(has_entry('id', context['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.access_feature(host='1.2.3.0/24')
@fixtures.access_feature(host='1.2.4.0/24')
def test_sorting_offset_limit(access_feature1, access_feature2):
    url = confd.access_features.get
    s.check_sorting(url, access_feature1, access_feature2, 'host', '1.2.')
    s.check_offset(url, access_feature1, access_feature2, 'host', '1.2.')
    s.check_limit(url, access_feature1, access_feature2, 'host', '1.2.')


@fixtures.access_feature(host='1.2.3.0/24')
def test_get(access_feature):
    response = confd.access_features(access_feature['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=access_feature['id'],
            host=access_feature['host'],
            feature='phonebook',
            enabled=True,
        ),
    )


def test_create_minimal_parameters():
    response = confd.access_features.post(host='1.2.3.0/24')
    response.assert_created('access_features')

    assert_that(response.item, has_entries(id=not_(empty())))

    confd.access_features(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {'host': '1.2.3.0/24', 'feature': 'phonebook', 'enabled': True}

    response = confd.access_features.post(**parameters)
    response.assert_created('access_features')

    assert_that(response.item, has_entries(**parameters))

    confd.access_features(response.item['id']).delete().assert_deleted()


@fixtures.access_feature(host='1.2.3.0/24')
def test_create_already_existing_access_feature(_):
    response = confd.access_features.post(
        {'host': '1.2.3.0/24', 'feature': 'phonebook'}
    )
    response.assert_match(400, e.resource_exists(resource='AccessFeatures'))


@fixtures.access_feature()
def test_edit_minimal_parameters(access_feature):
    response = confd.access_features(access_feature['id']).put()
    response.assert_updated()


@fixtures.access_feature()
def test_edit_all_parameters(access_feature):
    parameters = {'host': '1.2.3.0/24', 'feature': 'phonebook', 'enabled': False}

    response = confd.access_features(access_feature['id']).put(**parameters)
    response.assert_updated()

    response = confd.access_features(access_feature['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.access_feature(host='1.2.3.0/24')
@fixtures.access_feature(host='1.2.4.0/24')
def test_edit_host_feature_unavailable(access_feature1, access_feature2):
    response = confd.access_features(access_feature2['id']).put(host='1.2.3.0/24')
    response.assert_match(400, e.resource_exists(resource='AccessFeatures'))


@fixtures.access_feature(host='1.2.3.0/24')
def test_delete(access_feature):
    response = confd.access_features(access_feature['id']).delete()
    response.assert_deleted()
    response = confd.access_features(access_feature['id']).get()
    response.assert_match(404, e.not_found(resource='AccessFeatures'))


@fixtures.access_feature()
def test_restrict_only_master_tenant(access):
    response = confd.access_features.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.access_features.post(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.access_features(access['id']).get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.access_features(access['id']).put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.access_features(access['id']).delete(token=TOKEN_SUB_TENANT)
    response.assert_status(401)


@fixtures.access_feature(host='1.2.3.0/24')
def test_bus_events(access_feature):
    expected_headers = {}

    s.check_event(
        'access_feature_created',
        expected_headers,
        confd.access_features.post,
        {
            'host': '9.2.4.0/24',
            'feature': 'phonebook',
        },
    )
    s.check_event(
        'access_feature_edited',
        expected_headers,
        confd.access_features(access_feature['id']).put,
    )
    s.check_event(
        'access_feature_deleted',
        expected_headers,
        confd.access_features(access_feature['id']).delete,
    )
