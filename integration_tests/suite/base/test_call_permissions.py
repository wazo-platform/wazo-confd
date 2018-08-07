# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    all_of,
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
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


def test_get_errors():
    fake_get = confd.callpermissions(999999).get
    yield s.check_resource_not_found, fake_get, 'CallPermission'


def test_post_errors():
    url = confd.callpermissions.post
    for check in error_checks(url):
        yield check


@fixtures.call_permission()
def test_put_errors(call_permission):
    url = confd.callpermissions(call_permission['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', 'invalid_régèx!'
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'password', 123
    yield s.check_bogus_field_returns_error, url, 'password', True
    yield s.check_bogus_field_returns_error, url, 'password', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'password', {}
    yield s.check_bogus_field_returns_error, url, 'password', []
    yield s.check_bogus_field_returns_error, url, 'description', 123
    yield s.check_bogus_field_returns_error, url, 'description', True
    yield s.check_bogus_field_returns_error, url, 'description', {}
    yield s.check_bogus_field_returns_error, url, 'description', []
    yield s.check_bogus_field_returns_error, url, 'mode', 123
    yield s.check_bogus_field_returns_error, url, 'mode', None
    yield s.check_bogus_field_returns_error, url, 'mode', False
    yield s.check_bogus_field_returns_error, url, 'mode', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'enabled', None
    yield s.check_bogus_field_returns_error, url, 'enabled', 123
    yield s.check_bogus_field_returns_error, url, 'enabled', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'enabled', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', []
    yield s.check_bogus_field_returns_error, url, 'extensions', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'extensions', 123
    yield s.check_bogus_field_returns_error, url, 'extensions', True
    yield s.check_bogus_field_returns_error, url, 'extensions', None
    yield s.check_bogus_field_returns_error, url, 'extensions', {}


@fixtures.call_permission(name="search", password="123", description="SearchDesc", mode='deny', enabled=True)
@fixtures.call_permission(name="hidden", password="456", description="HiddenDesc", mode='allow', enabled=False)
def test_search(call_permission, hidden):
    url = confd.callpermissions
    searches = {
        'name': 'search',
        'description': 'Search',
        'mode': 'deny',
        'enabled': True,
    }

    for field, term in searches.items():
        yield check_search, url, call_permission, hidden, field, term


@fixtures.call_permission(name="sort1", description="Sort 1")
@fixtures.call_permission(name="sort2", description="Sort 2")
def test_sorting_offset_limit(call_permission1, call_permission2):
    url = confd.callpermissions.get
    yield s.check_sorting, url, call_permission1, call_permission2, 'name', 'sort'
    yield s.check_sorting, url, call_permission1, call_permission2, 'description', 'Sort'

    yield s.check_offset, url, call_permission1, call_permission2, 'name', 'sort'
    yield s.check_offset_legacy, url, call_permission1, call_permission2, 'name', 'sort'

    yield s.check_limit, url, call_permission1, call_permission2, 'name', 'sort'


def check_search(url, call_permission, hidden, field, term):
    response = url.get(search=term)

    expected_call_permission = has_item(has_entry(field, call_permission[field]))
    hidden_call_permission = is_not(has_item(has_entry(field, hidden[field])))
    assert_that(response.items, expected_call_permission)
    assert_that(response.items, hidden_call_permission)

    response = url.get(**{field: call_permission[field]})

    expected_call_permission = has_item(has_entry('id', call_permission['id']))
    hidden_call_permission = is_not(has_item(has_entry('id', hidden['id'])))
    assert_that(response.items, expected_call_permission)
    assert_that(response.items, hidden_call_permission)


@fixtures.call_permission(wazo_tenant=MAIN_TENANT)
@fixtures.call_permission(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.callpermissions.get(wazo_tenant=MAIN_TENANT)
    assert_that(
        response.items,
        all_of(has_item(main)), not_(has_item(sub)),
    )

    response = confd.callpermissions.get(wazo_tenant=SUB_TENANT)
    assert_that(
        response.items,
        all_of(has_item(sub), not_(has_item(main))),
    )

    response = confd.callpermissions.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(
        response.items,
        has_items(main, sub),
    )


@fixtures.call_permission(
    name="search",
    password="123",
    description="SearchDesc",
    mode='deny',
    enabled=True,
    extensions=['123', '456'],
)
def test_get(call_permission):
    response = confd.callpermissions(call_permission['id']).get()
    assert_that(response.item, has_entries(
        name='search',
        password='123',
        description='SearchDesc',
        mode='deny',
        enabled=True,
        extensions=['123', '456'],
        users=empty(),
        outcalls=empty(),
        groups=empty(),
    ))


@fixtures.call_permission(wazo_tenant=MAIN_TENANT)
@fixtures.call_permission(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.callpermissions(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='CallPermission'))

    response = confd.callpermissions(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.callpermissions.post(name='minimal')
    response.assert_created('callpermissions')

    assert_that(response.item, has_entries(
        tenant_uuid=MAIN_TENANT,
        name='minimal',
        password=None,
        description=None,
        mode='deny',
        enabled=True,
        extensions=[],
    ))


def test_create_all_parameters():
    parameters = {
        'name': 'allparameter',
        'password': '1234',
        'description': 'Create description',
        'mode': 'allow',
        'enabled': False,
        'extensions': ['123', '*456', '963'],
    }

    response = confd.callpermissions.post(**parameters)
    response.assert_created('callpermissions')
    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))


def test_create_without_name():
    response = confd.callpermissions.post()
    response.assert_status(400)


@fixtures.call_permission()
def test_create_2_call_permissions_with_same_name(call_permission):
    response = confd.callpermissions.post(name=call_permission['name'])
    response.assert_match(400, e.resource_exists('CallPermission'))


@fixtures.call_permission()
def test_create_with_invalid_mode(call_permission):
    response = confd.callpermissions.post(name=call_permission['name'], mode='invalidmode')
    response.assert_status(400)


def test_create_with_duplicate_extensions():
    parameters = {'name': 'duplicate_perm',
                  'extensions': ['123', '123', '456']}

    response = confd.callpermissions.post(**parameters)
    response.assert_created('callpermissions')
    assert_that(response.item, has_entries(name=parameters['name'], extensions=['123', '456']))


@fixtures.call_permission(name='name1', extension=['123'])
def test_edit_all_parameters(call_permission):
    parameters = {
        'name': 'second',
        'password': '1234',
        'description': 'Create description',
        'mode': 'allow',
        'enabled': False,
        'extensions': ['123', '*456', '963'],
    }

    response = confd.callpermissions(call_permission['id']).put(**parameters)
    response.assert_updated()

    response = confd.callpermissions(call_permission['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.call_permission(name='call_permission1')
@fixtures.call_permission(name='call_permission2')
def test_edit_with_same_name(first_call_permission, second_call_permission):
    response = confd.callpermissions(first_call_permission['id']).put(name=second_call_permission['name'])
    response.assert_match(400, e.resource_exists('CallPermission'))


@fixtures.call_permission(wazo_tenant=MAIN_TENANT)
@fixtures.call_permission(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.callpermissions(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='CallPermission'))

    response = confd.callpermissions(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.call_permission()
def test_delete(call_permission):
    response = confd.callpermissions(call_permission['id']).delete()
    response.assert_deleted()
