# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
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
    not_,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from . import confd


def test_get_errors():
    fake_paging = confd.pagings(999999).get
    s.check_resource_not_found(fake_paging, 'Paging')


def test_delete_errors():
    fake_paging = confd.pagings(999999).delete
    s.check_resource_not_found(fake_paging, 'Paging')


def test_post_errors():
    url = confd.pagings.post
    error_checks(url)


@fixtures.paging(number='724464')
def test_put_errors(paging):
    url = confd.pagings(paging['id']).put
    error_checks(url)


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', 1234)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'number', True)
    s.check_bogus_field_returns_error(url, 'number', 123)
    s.check_bogus_field_returns_error(url, 'number', 'invalid')
    s.check_bogus_field_returns_error(url, 'number', [])
    s.check_bogus_field_returns_error(url, 'number', {})
    s.check_bogus_field_returns_error(url, 'announce_caller', 'invalid')
    s.check_bogus_field_returns_error(url, 'announce_caller', None)
    s.check_bogus_field_returns_error(url, 'announce_caller', [])
    s.check_bogus_field_returns_error(url, 'announce_caller', {})
    s.check_bogus_field_returns_error(url, 'announce_sound', True)
    s.check_bogus_field_returns_error(url, 'announce_sound', 1234)
    s.check_bogus_field_returns_error(url, 'announce_sound', [])
    s.check_bogus_field_returns_error(url, 'announce_sound', {})
    s.check_bogus_field_returns_error(url, 'duplex', 'invalid')
    s.check_bogus_field_returns_error(url, 'duplex', None)
    s.check_bogus_field_returns_error(url, 'duplex', [])
    s.check_bogus_field_returns_error(url, 'duplex', {})
    s.check_bogus_field_returns_error(url, 'ignore_forward', 'invalid')
    s.check_bogus_field_returns_error(url, 'ignore_forward', None)
    s.check_bogus_field_returns_error(url, 'ignore_forward', [])
    s.check_bogus_field_returns_error(url, 'ignore_forward', {})
    s.check_bogus_field_returns_error(url, 'record', 'invalid')
    s.check_bogus_field_returns_error(url, 'record', None)
    s.check_bogus_field_returns_error(url, 'record', [])
    s.check_bogus_field_returns_error(url, 'record', {})
    s.check_bogus_field_returns_error(url, 'enabled', 'invalid')
    s.check_bogus_field_returns_error(url, 'enabled', None)
    s.check_bogus_field_returns_error(url, 'enabled', [])
    s.check_bogus_field_returns_error(url, 'enabled', {})

    unique_error_checks(url)


@fixtures.paging(number='123')
def unique_error_checks(url, paging):
    s.check_bogus_field_returns_error(url, 'number', paging['number'])


@fixtures.paging(name='search', number='123', announce_sound='search')
@fixtures.paging(name='hidden', number='456', announce_sound='hidden')
def test_search(paging, hidden):
    url = confd.pagings
    searches = {'name': 'search', 'number': '123', 'announce_sound': 'search'}

    for field, term in searches.items():
        check_search(url, paging, hidden, field, term)


def check_search(url, paging, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, paging[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: paging[field]})
    assert_that(response.items, has_item(has_entry('id', paging['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.paging(name='sort1')
@fixtures.paging(name='sort2')
def test_sort_offset_limit(paging1, paging2):
    url = confd.pagings.get
    s.check_sorting(url, paging1, paging2, 'name', 'sort')

    s.check_offset(url, paging1, paging2, 'name', 'sort')
    s.check_limit(url, paging1, paging2, 'name', 'sort')


@fixtures.paging(wazo_tenant=MAIN_TENANT)
@fixtures.paging(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.pagings.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.pagings.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.pagings.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.paging()
def test_get(paging):
    response = confd.pagings(paging['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=paging['id'],
            name=paging['name'],
            number=paging['number'],
            announce_caller=paging['announce_caller'],
            announce_sound=paging['announce_sound'],
            caller_notification=paging['caller_notification'],
            duplex=paging['duplex'],
            ignore_forward=paging['ignore_forward'],
            record=paging['record'],
            enabled=paging['enabled'],
        ),
    )


@fixtures.paging(wazo_tenant=MAIN_TENANT)
@fixtures.paging(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.pagings(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Paging'))

    response = confd.pagings(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.pagings.post(number='123')
    response.assert_created('pagings')

    assert_that(response.item, has_entries(id=not_(empty()), tenant_uuid=MAIN_TENANT))

    confd.pagings(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'MyPaging',
        'number': '123',
        'announce_caller': False,
        'announce_sound': 'sound',
        'caller_notification': True,
        'duplex': True,
        'ignore_forward': True,
        'record': True,
        'enabled': False,
    }

    response = confd.pagings.post(**parameters)
    response.assert_created('pagings')
    response = confd.pagings(response.item['id']).get()

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.pagings(response.item['id']).delete().assert_deleted()


@fixtures.paging()
def test_edit_minimal_parameters(paging):
    response = confd.pagings(paging['id']).put()
    response.assert_updated()


@fixtures.paging()
def test_edit_all_parameters(paging):
    parameters = {
        'name': 'MyPaging',
        'number': '123',
        'announce_caller': False,
        'announce_sound': 'sound',
        'caller_notification': True,
        'duplex': True,
        'ignore_forward': True,
        'record': True,
        'enabled': False,
    }

    response = confd.pagings(paging['id']).put(**parameters)
    response.assert_updated()

    response = confd.pagings(paging['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.paging(wazo_tenant=MAIN_TENANT)
@fixtures.paging(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.pagings(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Paging'))

    response = confd.pagings(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.paging()
def test_delete(paging):
    response = confd.pagings(paging['id']).delete()
    response.assert_deleted()
    response = confd.pagings(paging['id']).get()
    response.assert_match(404, e.not_found(resource='Paging'))


@fixtures.paging(wazo_tenant=MAIN_TENANT)
@fixtures.paging(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.pagings(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Paging'))

    response = confd.pagings(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.paging(number='667')
def test_bus_events(paging):
    url = confd.pagings(paging['id'])
    headers = {'tenant_uuid': paging['tenant_uuid']}

    s.check_event('paging_created', headers, confd.pagings.post, {'number': '666'})
    s.check_event('paging_edited', headers, url.put)
    s.check_event('paging_deleted', headers, url.delete)
