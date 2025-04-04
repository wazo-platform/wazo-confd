# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    none,
    not_,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd


def test_get_errors():
    fake_get = confd.callpickups(999999).get
    s.check_resource_not_found(fake_get, 'CallPickup')


def test_post_errors():
    url = confd.callpickups.post
    error_checks(url)


@fixtures.call_pickup()
def test_put_errors(call_pickup):
    url = confd.callpickups(call_pickup['id']).put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', 123)
    s.check_bogus_field_returns_error(url, 'name', None)
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'description', 123)
    s.check_bogus_field_returns_error(url, 'description', True)
    s.check_bogus_field_returns_error(url, 'description', {})
    s.check_bogus_field_returns_error(url, 'description', [])
    s.check_bogus_field_returns_error(url, 'enabled', None)
    s.check_bogus_field_returns_error(url, 'enabled', 123)
    s.check_bogus_field_returns_error(url, 'enabled', 'invalid')
    s.check_bogus_field_returns_error(url, 'enabled', {})
    s.check_bogus_field_returns_error(url, 'enabled', [])

    unique_error_checks(url)


@fixtures.call_pickup(name='unique')
def unique_error_checks(url, call_pickup):
    s.check_bogus_field_returns_error(url, 'name', call_pickup['name'])


@fixtures.call_pickup(wazo_tenant=MAIN_TENANT)
@fixtures.call_pickup(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.callpickups.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.callpickups.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.callpickups.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.call_pickup(name="search", description="SearchDesc")
@fixtures.call_pickup(name="hidden", description="HiddenDesc")
def test_search(call_pickup, hidden):
    url = confd.callpickups
    searches = {'name': 'search', 'description': 'Search'}

    for field, term in searches.items():
        check_search(url, call_pickup, hidden, field, term)


def check_search(url, call_pickup, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, call_pickup[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: call_pickup[field]})

    assert_that(response.items, has_item(has_entry('id', call_pickup['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.call_pickup(name="sort1", description="Sort 1")
@fixtures.call_pickup(name="sort2", description="Sort 2")
def test_sorting_offset_limit(call_pickup1, call_pickup2):
    url = confd.callpickups.get
    s.check_sorting(url, call_pickup1, call_pickup2, 'name', 'sort')
    s.check_sorting(url, call_pickup1, call_pickup2, 'description', 'Sort')

    s.check_offset(url, call_pickup1, call_pickup2, 'name', 'sort')
    s.check_limit(url, call_pickup1, call_pickup2, 'name', 'sort')


@fixtures.call_pickup()
def test_get(call_pickup):
    response = confd.callpickups(call_pickup['id']).get()
    assert_that(
        response.item,
        has_entries(
            name=call_pickup['name'],
            description=none(),
            enabled=True,
            interceptors=has_entries(groups=empty(), users=empty()),
            targets=has_entries(groups=empty(), users=empty()),
        ),
    )


@fixtures.call_pickup(wazo_tenant=MAIN_TENANT)
@fixtures.call_pickup(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.callpickups(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='CallPickup'))

    response = confd.callpickups(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.callpickups.post(name='minimal')
    response.assert_created('callpickups')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, id=not_(empty())))

    confd.callpickups(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'allparameter',
        'description': 'Create description',
        'enabled': False,
    }

    response = confd.callpickups.post(**parameters)
    response.assert_created('callpickups')
    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))
    confd.callpickups(response.item['id']).delete().assert_deleted()


def test_create_without_name():
    response = confd.callpickups.post()
    response.assert_status(400)


@fixtures.call_pickup()
def test_edit_minimal_parameters(call_pickup):
    response = confd.callpickups(call_pickup['id']).put()
    response.assert_updated()


@fixtures.call_pickup()
def test_edit_all_parameters(call_pickup):
    parameters = {
        'name': 'editallparameter',
        'description': 'Create description',
        'enabled': False,
    }

    response = confd.callpickups(call_pickup['id']).put(**parameters)
    response.assert_updated()

    response = confd.callpickups(call_pickup['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.call_pickup(wazo_tenant=MAIN_TENANT)
@fixtures.call_pickup(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.callpickups(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='CallPickup'))

    response = confd.callpickups(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.call_pickup()
def test_delete(call_pickup):
    response = confd.callpickups(call_pickup['id']).delete()
    response.assert_deleted()
    confd.callpickups(call_pickup['id']).get().assert_status(404)


@fixtures.call_pickup(wazo_tenant=MAIN_TENANT)
@fixtures.call_pickup(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.callpickups(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='CallPickup'))

    response = confd.callpickups(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()
