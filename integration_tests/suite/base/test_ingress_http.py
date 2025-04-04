# Copyright 2024-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_exactly,
    empty,
    has_entries,
    has_entry,
    has_items,
    is_,
    is_not,
    not_,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd

FAKE_UUID = '99999999-9999-4999-9999-999999999999'


def test_post_errors():
    url = confd.ingresses.http.post
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'uri', 123)
    s.check_bogus_field_returns_error(url, 'uri', None)
    s.check_bogus_field_returns_error(url, 'uri', True)
    s.check_bogus_field_returns_error(url, 'uri', {})
    s.check_bogus_field_returns_error(url, 'uri', [])
    s.check_bogus_field_returns_error(url, 'uri', 'a' * 1025)


def test_create_all_parameters():
    parameters = {'uri': 'http://all:10080'}

    response = confd.ingresses.http.post(**parameters)
    response.assert_created('http')
    try:
        assert_that(
            response.item,
            has_entries(
                uuid=not_(empty()),
                uri='http://all:10080',
                tenant_uuid=MAIN_TENANT,
            ),
        )
    finally:
        confd.ingresses.http(response.item['uuid']).delete()


@fixtures.ingress_http()
def test_create_multiple_config_for_a_tenant(ingress_http):
    response = confd.ingresses.http.post({'uri': 'new'})
    response.assert_match(400, e.resource_exists(resource='IngressHTTP'))


def check_search(url, ingress_http, hidden, field, term):
    # Searches are done with recurse True because there's only one ingress_http for a tenant
    response = url.get(search=term, recurse=True)
    assert_that(response.items, has_items(has_entry(field, ingress_http[field])))
    assert_that(response.items, is_not(has_items(has_entry(field, hidden[field]))))

    response = url.get(recurse=True, **{field: ingress_http[field]})
    assert_that(response.items, has_items(has_entries(uuid=ingress_http['uuid'])))
    assert_that(response.items, is_not(has_items(has_entries(uuid=hidden['uuid']))))


@fixtures.ingress_http(uri='search', wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(uri='hidden', wazo_tenant=SUB_TENANT)
def test_search(ingress_http, hidden):
    url = confd.ingresses.http
    searches = {'uri': 'search'}

    for field, term in searches.items():
        check_search(url, ingress_http, hidden, field, term)


def test_list_errors():
    response = confd.ingresses.http.get(view='invalid')
    response.assert_status(400)


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.ingresses.http.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_items(main)), not_(has_items(sub)))

    response = confd.ingresses.http.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_items(sub), not_(has_items(main))))

    response = confd.ingresses.http.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT, uri='main')
@fixtures.ingress_http(wazo_tenant=SUB_TENANT, uri='sub')
def test_list_fallback_tenant(main, sub):
    response = confd.ingresses.http.get(wazo_tenant=SUB_TENANT, view='default')
    assert_that(
        response.items,
        contains_exactly(has_entries(uri='sub')),
    )
    response = confd.ingresses.http.get(wazo_tenant=SUB_TENANT, view='fallback')
    assert_that(
        response.items,
        contains_exactly(has_entries(uri='sub')),
    )

    response = confd.ingresses.http(sub['uuid']).delete()
    response.assert_deleted()

    response = confd.ingresses.http.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, has_items(main))
    assert_that(len(response.items), is_(1))

    response = confd.ingresses.http.get(wazo_tenant=SUB_TENANT, view='fallback')
    assert_that(response.items, has_items(main))
    assert_that(len(response.items), is_(1))

    response = confd.ingresses.http.get(wazo_tenant=SUB_TENANT, view='default')
    assert_that(len(response.items), is_(0))

    response = confd.ingresses.http.get(wazo_tenant=SUB_TENANT)
    assert_that(len(response.items), is_(0))


@fixtures.ingress_http(uri='sort1', wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(uri='sort2', wazo_tenant=SUB_TENANT)
def test_sorting_offset_limit(ingress_http1, ingress_http2):
    common_args = {'order': 'uri', 'recurse': True}
    url = confd.ingresses.http.get

    response = url(direction='asc', **common_args)
    assert_that(response.items, contains(ingress_http1, ingress_http2))

    response = url(direction='desc', **common_args)
    assert_that(response.items, contains(ingress_http2, ingress_http1))

    response = url(offset=1, **common_args)
    assert_that(response.items, contains(ingress_http2))

    response = url(limit=1, **common_args)
    assert_that(response.items, contains(ingress_http1))


def test_get_errors():
    fake_ingress_http = confd.ingresses.http(FAKE_UUID).get
    s.check_resource_not_found(fake_ingress_http, 'IngressHTTP')


@fixtures.ingress_http()
def test_get(ingress_http):
    response = confd.ingresses.http(ingress_http['uuid']).get()
    assert_that(
        response.item,
        has_entries(
            uuid=ingress_http['uuid'],
            uri=ingress_http['uri'],
            tenant_uuid=ingress_http['tenant_uuid'],
        ),
    )


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.ingresses.http(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='IngressHTTP'))

    response = confd.ingresses.http(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


@fixtures.ingress_http()
def test_put_errors(ingress_http):
    response = confd.ingresses.http(FAKE_UUID).put(uri='valid')
    response.assert_match(404, e.not_found(resource='IngressHTTP'))

    url = confd.ingresses.http(ingress_http['uuid']).put
    error_checks(url)


@fixtures.ingress_http()
def test_edit_minimal_parameters(ingress_http):
    response = confd.ingresses.http(ingress_http['uuid']).put(uri='minimal')
    response.assert_updated()

    result = confd.ingresses.http(ingress_http['uuid']).get()
    assert_that(
        result.item,
        has_entries(
            tenant_uuid=MAIN_TENANT,
            uuid=ingress_http['uuid'],
            uri='minimal',
        ),
    )


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.ingresses.http(main['uuid']).put(
        uri='valid', wazo_tenant=SUB_TENANT
    )
    response.assert_match(404, e.not_found('IngressHTTP'))

    response = confd.ingresses.http(sub['uuid']).put(
        uri='valid', wazo_tenant=MAIN_TENANT
    )
    response.assert_updated()


def test_delete_errors():
    fake_ingress_http = confd.ingresses.http(FAKE_UUID).delete
    s.check_resource_not_found(fake_ingress_http, 'IngressHTTP')


@fixtures.ingress_http()
def test_delete(ingress_http):
    response = confd.ingresses.http(ingress_http['uuid']).delete()
    response.assert_deleted()

    confd.ingresses.http(ingress_http['uuid']).get().assert_status(404)


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.ingresses.http(main['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='IngressHTTP'))

    response = confd.ingresses.http(sub['uuid']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


def test_bus_events():
    headers = {'tenant_uuid': MAIN_TENANT}
    res = None

    def post():
        nonlocal res
        res = confd.ingresses.http.post(uri='post')

    s.check_event('ingress_http_created', headers, post)

    url = confd.ingresses.http(res.item['uuid'])
    s.check_event('ingress_http_edited', headers, url.put, {'uri': 'put'})
    s.check_event('ingress_http_deleted', headers, url.delete)
