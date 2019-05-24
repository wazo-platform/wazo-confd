# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_items,
    none,
    not_,
)

from . import confd
from ..helpers import (
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import (
    MAIN_TENANT,
    SUB_TENANT,
)

ALL_OPTIONS = [
    ["cid_name", "cid_name"],
    ["cid_num", "cid_num"],
    ["allow", "allow"],
    ["disallow", "disallow"]
]


def test_get_errors():
    fake_sccp_get = confd.endpoints.sccp(999999).get
    yield s.check_resource_not_found, fake_sccp_get, 'SCCPEndpoint'


def test_delete_errors():
    fake_sccp = confd.endpoints.sccp(999999).delete
    yield s.check_resource_not_found, fake_sccp, 'SCCPEndpoint'


def test_post_errors():
    url = confd.endpoints.sccp.post
    for check in error_checks(url):
        yield check


@fixtures.sccp()
def test_put_errors(sccp):
    url = confd.endpoints.sccp(sccp['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', {}
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [None]
    yield s.check_bogus_field_returns_error, url, 'options', ['string', 'string']
    yield s.check_bogus_field_returns_error, url, 'options', [123, 123]
    yield s.check_bogus_field_returns_error, url, 'options', ['string', 123]
    yield s.check_bogus_field_returns_error, url, 'options', [[]]
    yield s.check_bogus_field_returns_error, url, 'options', [{'key': 'value'}]
    yield s.check_bogus_field_returns_error, url, 'options', [['missing_value']]
    yield s.check_bogus_field_returns_error, url, 'options', [['too', 'much', 'value']]
    yield s.check_bogus_field_returns_error, url, 'options', [['wrong_value', 1234]]
    yield s.check_bogus_field_returns_error, url, 'options', [['none_value', None]]


@fixtures.sccp()
def test_get(sccp):
    response = confd.endpoints.sccp(sccp['id']).get()
    assert_that(response.item, has_entries(
        line=none(),
    ))


@fixtures.sccp()
@fixtures.sccp()
def test_list(sccp1, sccp2):
    response = confd.endpoints.sccp.get()
    assert_that(response.items, has_items(
        has_entry('id', sccp1['id']),
        has_entry('id', sccp2['id']),
    ))


@fixtures.sccp(wazo_tenant=MAIN_TENANT)
@fixtures.sccp(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.endpoints.sccp.get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.items,
        all_of(has_items(main)), not_(has_items(sub)),
    )

    response = confd.endpoints.sccp.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(has_items(sub), not_(has_items(main))),
    )

    response = confd.endpoints.sccp.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(
        response.items,
        has_items(main, sub),
    )


@fixtures.sccp(wazo_tenant=MAIN_TENANT)
@fixtures.sccp(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.endpoints.sccp(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='SCCPEndpoint'))

    response = confd.endpoints.sccp(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.endpoints.sccp.post()

    response.assert_created('endpoint_sccp', location='endpoints/sccp')
    assert_that(response.item, has_entries(
        tenant_uuid=MAIN_TENANT,
        options=empty(),
    ))


def test_create_all_parameters():
    response = confd.endpoints.sccp.post(options=ALL_OPTIONS)

    assert_that(response.item, has_entries(
        tenant_uuid=MAIN_TENANT,
        options=has_items(*ALL_OPTIONS),
    ))


@fixtures.sccp(options=[["allow", "alaw"], ["disallow", "all"]])
def test_update_options(sccp):
    options = [
        ["allow", "g723"],
        ["disallow", "opus"]
    ]

    response = confd.endpoints.sccp(sccp['id']).put(options=options)
    response.assert_updated()

    response = confd.endpoints.sccp(sccp['id']).get()
    assert_that(response.item['options'], has_items(*options))


@fixtures.sccp(wazo_tenant=MAIN_TENANT)
@fixtures.sccp(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.endpoints.sccp(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='SCCPEndpoint'))

    response = confd.endpoints.sccp(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.sccp()
def test_delete(sccp):
    response = confd.endpoints.sccp(sccp['id']).delete()
    response.assert_deleted()


@fixtures.sccp(wazo_tenant=MAIN_TENANT)
@fixtures.sccp(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.endpoints.sccp(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='SCCPEndpoint'))

    response = confd.endpoints.sccp(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()
