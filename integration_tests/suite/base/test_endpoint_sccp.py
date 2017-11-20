# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from ..helpers import fixtures
from ..helpers import scenarios as s

from hamcrest import assert_that, has_entries, has_items, \
    instance_of, contains, has_entry
from . import confd

ALL_OPTIONS = [
    ["cid_name", "cid_name"],
    ["cid_num", "cid_num"],
    ["allow", "allow"],
    ["disallow", "disallow"]
]


def test_get_errors():
    fake_sccp_get = confd.endpoints.sccp(999999).get
    yield s.check_resource_not_found, fake_sccp_get, 'SCCPEndpoint'


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
def test_delete_errors(sccp):
    url = confd.endpoints.sccp(sccp['id'])
    url.delete()
    yield s.check_resource_not_found, url.get, 'SCCPEndpoint'


@fixtures.sccp()
def test_get(sccp):
    expected = has_entries({'id': instance_of(int),
                            'options': contains(),
                            'line': None})

    response = confd.endpoints.sccp(sccp['id']).get()
    assert_that(response.item, expected)


@fixtures.sccp()
@fixtures.sccp()
def test_list(sccp1, sccp2):
    expected = has_items(has_entry('id', sccp1['id']),
                         has_entry('id', sccp2['id']))

    response = confd.endpoints.sccp.get()
    assert_that(response.items, expected)


def test_create_sccp_with_minimal_parameters():
    expected = has_entries({'id': instance_of(int),
                            'options': contains()})

    response = confd.endpoints.sccp.post()

    response.assert_created('endpoint_sccp', location='endpoints/sccp')
    assert_that(response.item, expected)


def test_create_sccp_with_all_parameters():
    expected = has_entries({'options': has_items(*ALL_OPTIONS)
                            })

    response = confd.endpoints.sccp.post(options=ALL_OPTIONS)

    assert_that(response.item, expected)


@fixtures.sccp(options=[["allow", "alaw"], ["disallow", "all"]])
def test_update_options(sccp):
    options = [
        ["allow", "g723"],
        ["disallow", "opus"]
    ]

    url = confd.endpoints.sccp(sccp['id'])
    response = url.put(options=options)
    response.assert_updated()

    response = url.get()
    assert_that(response.item['options'], has_items(*options))


@fixtures.sccp()
def test_delete_sccp(sccp):
    response = confd.endpoints.sccp(sccp['id']).delete()
    response.assert_deleted()
