# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains_inanyorder,
    empty,
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
from . import BaseIntegrationTest, confd


def test_get_errors():
    fake_get = confd.callpermissions(999999).get
    s.check_resource_not_found(fake_get, 'CallPermission')


def test_post_errors():
    url = confd.callpermissions
    error_checks(url.post)
    s.check_missing_body_returns_error(url, 'POST')


@fixtures.call_permission()
def test_put_errors(call_permission):
    url = confd.callpermissions(call_permission['id'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', 123)
    s.check_bogus_field_returns_error(url, 'name', None)
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', 'a' * 129)
    s.check_bogus_field_returns_error(url, 'name', '')
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'password', 123)
    s.check_bogus_field_returns_error(url, 'password', True)
    s.check_bogus_field_returns_error(url, 'password', 'invalid')
    s.check_bogus_field_returns_error(url, 'password', {})
    s.check_bogus_field_returns_error(url, 'password', [])
    s.check_bogus_field_returns_error(url, 'description', 123)
    s.check_bogus_field_returns_error(url, 'description', True)
    s.check_bogus_field_returns_error(url, 'description', {})
    s.check_bogus_field_returns_error(url, 'description', [])
    s.check_bogus_field_returns_error(url, 'mode', 123)
    s.check_bogus_field_returns_error(url, 'mode', None)
    s.check_bogus_field_returns_error(url, 'mode', False)
    s.check_bogus_field_returns_error(url, 'mode', 'invalid')
    s.check_bogus_field_returns_error(url, 'enabled', None)
    s.check_bogus_field_returns_error(url, 'enabled', 123)
    s.check_bogus_field_returns_error(url, 'enabled', 'invalid')
    s.check_bogus_field_returns_error(url, 'enabled', {})
    s.check_bogus_field_returns_error(url, 'enabled', [])
    s.check_bogus_field_returns_error(url, 'extensions', 'invalid')
    s.check_bogus_field_returns_error(url, 'extensions', 123)
    s.check_bogus_field_returns_error(url, 'extensions', True)
    s.check_bogus_field_returns_error(url, 'extensions', None)
    s.check_bogus_field_returns_error(url, 'extensions', {})


@fixtures.call_permission(
    name="search", password="123", description="SearchDesc", mode='deny', enabled=True
)
@fixtures.call_permission(
    name="hidden", password="456", description="HiddenDesc", mode='allow', enabled=False
)
def test_search(call_permission, hidden):
    url = confd.callpermissions
    searches = {
        'name': 'search',
        'description': 'Search',
        'mode': 'deny',
        'enabled': True,
    }

    for field, term in searches.items():
        check_search(url, call_permission, hidden, field, term)


@fixtures.call_permission(name="sort1", description="Sort 1")
@fixtures.call_permission(name="sort2", description="Sort 2")
def test_sorting_offset_limit(call_permission1, call_permission2):
    url = confd.callpermissions.get
    s.check_sorting(url, call_permission1, call_permission2, 'name', 'sort')
    s.check_sorting(url, call_permission1, call_permission2, 'description', 'Sort')

    s.check_offset(url, call_permission1, call_permission2, 'name', 'sort')
    s.check_limit(url, call_permission1, call_permission2, 'name', 'sort')


def check_search(url, call_permission, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, call_permission[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: call_permission[field]})
    assert_that(response.items, has_item(has_entry('id', call_permission['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.call_permission(wazo_tenant=MAIN_TENANT)
@fixtures.call_permission(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.callpermissions.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.callpermissions.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.callpermissions.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


# Note: Until we have a better way to mesure query performance,
# this test makes sure we are using joinedload instead of lazyloading
@fixtures.call_permission(wazo_tenant=MAIN_TENANT)
def test_list_db_requests(*_):
    expected_request_count = 1 + 4 + 1  # 1 list with 4 selectin + 1 count
    s.check_db_requests(
        BaseIntegrationTest,
        confd.callpermissions.get,
        nb_requests=expected_request_count,
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
    assert_that(
        response.item,
        has_entries(
            name='search',
            password='123',
            description='SearchDesc',
            mode='deny',
            enabled=True,
            extensions=contains_inanyorder('123', '456'),
            users=empty(),
            outcalls=empty(),
            groups=empty(),
        ),
    )


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

    assert_that(
        response.item,
        has_entries(
            tenant_uuid=MAIN_TENANT,
            name='minimal',
            password=None,
            description=None,
            mode='deny',
            enabled=True,
            extensions=[],
        ),
    )


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
    parameters['extensions'] = contains_inanyorder(*parameters['extensions'])
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
    response = confd.callpermissions.post(
        name=call_permission['name'], mode='invalidmode'
    )
    response.assert_status(400)


def test_create_with_duplicate_extensions():
    parameters = {'name': 'duplicate_perm', 'extensions': ['123', '123', '456']}

    response = confd.callpermissions.post(**parameters)
    response.assert_created('callpermissions')
    assert_that(
        response.item,
        has_entries(
            name=parameters['name'], extensions=contains_inanyorder('123', '456')
        ),
    )


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
    parameters['extensions'] = contains_inanyorder(*parameters['extensions'])
    assert_that(response.item, has_entries(parameters))


@fixtures.call_permission(name='call_permission1')
@fixtures.call_permission(name='call_permission2')
def test_edit_with_same_name(first_call_permission, second_call_permission):
    response = confd.callpermissions(first_call_permission['id']).put(
        name=second_call_permission['name']
    )
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


@fixtures.call_permission(wazo_tenant=MAIN_TENANT)
@fixtures.call_permission(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.callpermissions(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='CallPermission'))

    response = confd.callpermissions(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()
