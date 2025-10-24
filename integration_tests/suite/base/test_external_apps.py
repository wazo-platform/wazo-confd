# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import json

from hamcrest import (
    all_of,
    assert_that,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd


def test_get_errors():
    fake_external_app = confd.external.apps('invalid').get
    s.check_resource_not_found(fake_external_app, 'ExternalApp')


def test_delete_errors():
    fake_external_app = confd.external.apps('invalid').delete
    s.check_resource_not_found(fake_external_app, 'ExternalApp')


@fixtures.external_app(name='unique')
def test_post_errors(external_app):
    url = confd.external.apps.myapp
    error_checks(url.post)
    s.check_missing_body_returns_error(url, 'POST')

    url = confd.external.apps(s.random_string(129))
    s.check_bogus_field_returns_error(url.post, 'name', s.random_string(129))

    url = confd.external.apps('unique')
    s.check_bogus_field_returns_error(url.post, 'name', 'unique')


@fixtures.external_app()
def test_put_errors(external_app):
    url = confd.external.apps(external_app['name'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'label', True)
    s.check_bogus_field_returns_error(url, 'label', 1234)
    s.check_bogus_field_returns_error(url, 'label', s.random_string(257))
    s.check_bogus_field_returns_error(url, 'label', [])
    s.check_bogus_field_returns_error(url, 'label', {})
    s.check_bogus_field_returns_error(url, 'configuration', True)
    s.check_bogus_field_returns_error(url, 'configuration', json.dumps('invalid'))
    s.check_bogus_field_returns_error(url, 'configuration', json.dumps(1234))
    s.check_bogus_field_returns_error(url, 'configuration', [])


@fixtures.external_app(wazo_tenant=MAIN_TENANT)
@fixtures.external_app(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.external.apps.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.external.apps.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.external.apps.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.external_app(name='search')
@fixtures.external_app(name='hidden')
def test_search(external_app, hidden):
    url = confd.external.apps
    searches = {'name': 'search'}

    for field, term in searches.items():
        check_search(url, external_app, hidden, field, term)


def check_search(url, external_app, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, external_app[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: external_app[field]})
    assert_that(response.items, has_item(has_entry('name', external_app['name'])))
    assert_that(response.items, is_not(has_item(has_entry('name', hidden['name']))))


@fixtures.external_app(name='sort1')
@fixtures.external_app(name='sort2')
def test_sort_offset_limit(external_app1, external_app2):
    url = confd.external.apps.get
    s.check_sorting(url, external_app1, external_app2, 'name', 'sort', 'name')

    s.check_offset(url, external_app1, external_app2, 'name', 'sort', 'name')
    s.check_limit(url, external_app1, external_app2, 'name', 'sort', 'name')


@fixtures.external_app()
def test_get(external_app):
    response = confd.external.apps(external_app['name']).get()
    assert_that(
        response.item,
        has_entries(
            tenant_uuid=external_app['tenant_uuid'],
            name=external_app['name'],
            label=external_app['label'],
            configuration=external_app['configuration'],
        ),
    )


@fixtures.external_app(wazo_tenant=MAIN_TENANT)
@fixtures.external_app(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.external.apps(main['name']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='ExternalApp'))

    response = confd.external.apps(sub['name']).get(wazo_tenant=MAIN_TENANT)
    response.assert_match(404, e.not_found(resource='ExternalApp'))


def test_create_minimal_parameters():
    response = confd.external.apps.myname.post()
    response.assert_created('external_apps', location='external/apps')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT))

    confd.external.apps(response.item['name']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'MyApp',
        'label': 'My app label',
        'configuration': {'key': {'subkey': 'value'}},
    }

    response = confd.external.apps(parameters['name']).post(**parameters)
    response.assert_created('external_apps', location='external/apps')
    response = confd.external.apps(response.item['name']).get()

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.external.apps(response.item['name']).delete().assert_deleted()


@fixtures.external_app(wazo_tenant=MAIN_TENANT)
def test_create_multi_tenant_with_same_name(main):
    response = confd.external.apps(main['name']).post(wazo_tenant=SUB_TENANT)
    response.assert_created('external_apps', location='external/apps')

    confd.external.apps(main['name']).delete().assert_deleted()


@fixtures.external_app()
def test_edit_minimal_parameters(external_app):
    response = confd.external.apps(external_app['name']).put()
    response.assert_updated()


@fixtures.external_app()
def test_edit_all_parameters(external_app):
    parameters = {
        'label': 'My app label',
        'configuration': {'key': {'subkey': 'value'}},
    }

    response = confd.external.apps(external_app['name']).put(**parameters)
    response.assert_updated()

    response = confd.external.apps(external_app['name']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.external_app(wazo_tenant=MAIN_TENANT)
@fixtures.external_app(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.external.apps(main['name']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='ExternalApp'))

    response = confd.external.apps(sub['name']).put(wazo_tenant=MAIN_TENANT)
    response.assert_match(404, e.not_found(resource='ExternalApp'))


@fixtures.external_app()
def test_delete(external_app):
    response = confd.external.apps(external_app['name']).delete()
    response.assert_deleted()
    response = confd.external.apps(external_app['name']).get()
    response.assert_match(404, e.not_found(resource='ExternalApp'))


@fixtures.external_app(wazo_tenant=MAIN_TENANT)
@fixtures.external_app(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.external.apps(main['name']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='ExternalApp'))

    response = confd.external.apps(sub['name']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_match(404, e.not_found(resource='ExternalApp'))


def test_bus_events():
    url = confd.external.apps.myname
    headers = {'tenant_uuid': MAIN_TENANT}

    s.check_event('external_app_created', headers, url.post)
    s.check_event('external_app_edited', headers, url.put)
    s.check_event('external_app_deleted', headers, url.delete)
