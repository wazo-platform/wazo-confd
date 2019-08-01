# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
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
    fake_get = confd.callpickups(999999).get
    s.check_resource_not_found(fake_get, 'CallPickup')


def test_post_errors():
    url = confd.callpickups.post
    error_checks(url)


def test_put_errors():
    with fixtures.call_pickup() as call_pickup:
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


def unique_error_checks(url):
    with fixtures.call_pickup(name='unique') as call_pickup:
        s.check_bogus_field_returns_error(url, 'name', call_pickup['name'])



def test_list_multi_tenant():
    with fixtures.call_pickup(wazo_tenant=MAIN_TENANT) as main, fixtures.call_pickup(wazo_tenant=SUB_TENANT) as sub:
        response = confd.callpickups.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            all_of(has_item(main)), not_(has_item(sub)),
        )

        response = confd.callpickups.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(has_item(sub), not_(has_item(main))),
        )

        response = confd.callpickups.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(
            response.items,
            has_items(main, sub),
        )



def test_search():
    with fixtures.call_pickup(name="search", description="SearchDesc") as call_pickup, fixtures.call_pickup(name="hidden", description="HiddenDesc") as hidden:
        url = confd.callpickups
        searches = {
            'name': 'search',
            'description': 'Search',
        }

        for field, term in searches.items():
            check_search(url, call_pickup, hidden, field, term)



def check_search(url, call_pickup, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, call_pickup[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: call_pickup[field]})

    assert_that(response.items, has_item(has_entry('id', call_pickup['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def test_sorting_offset_limit():
    with fixtures.call_pickup(name="sort1", description="Sort 1") as call_pickup1, fixtures.call_pickup(name="sort2", description="Sort 2") as call_pickup2:
        url = confd.callpickups.get
        s.check_sorting(url, call_pickup1, call_pickup2, 'name', 'sort')
        s.check_sorting(url, call_pickup1, call_pickup2, 'description', 'Sort')

        s.check_offset(url, call_pickup1, call_pickup2, 'name', 'sort')
        s.check_offset_legacy(url, call_pickup1, call_pickup2, 'name', 'sort')

        s.check_limit(url, call_pickup1, call_pickup2, 'name', 'sort')



def test_get():
    with fixtures.call_pickup() as call_pickup:
        response = confd.callpickups(call_pickup['id']).get()
        assert_that(response.item, has_entries(
            name=call_pickup['name'],
            description=none(),
            enabled=True,
            interceptors=has_entries(
                groups=empty(),
                users=empty(),
            ),
            targets=has_entries(
                groups=empty(),
                users=empty(),
            ),
        ))



def test_get_multi_tenant():
    with fixtures.call_pickup(wazo_tenant=MAIN_TENANT) as main, fixtures.call_pickup(wazo_tenant=SUB_TENANT) as sub:
        response = confd.callpickups(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='CallPickup'))

        response = confd.callpickups(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(**sub))



def test_create_minimal_parameters():
    response = confd.callpickups.post(
        name='minimal',
    )
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


def test_edit_minimal_parameters():
    with fixtures.call_pickup() as call_pickup:
        response = confd.callpickups(call_pickup['id']).put()
        response.assert_updated()



def test_edit_all_parameters():
    with fixtures.call_pickup() as call_pickup:
        parameters = {
            'name': 'editallparameter',
            'description': 'Create description',
            'enabled': False,
        }

        response = confd.callpickups(call_pickup['id']).put(**parameters)
        response.assert_updated()

        response = confd.callpickups(call_pickup['id']).get()
        assert_that(response.item, has_entries(parameters))



def test_edit_multi_tenant():
    with fixtures.call_pickup(wazo_tenant=MAIN_TENANT) as main, fixtures.call_pickup(wazo_tenant=SUB_TENANT) as sub:
        response = confd.callpickups(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='CallPickup'))

        response = confd.callpickups(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_delete():
    with fixtures.call_pickup() as call_pickup:
        response = confd.callpickups(call_pickup['id']).delete()
        response.assert_deleted()
        confd.callpickups(call_pickup['id']).get().assert_status(404)



def test_delete_multi_tenant():
    with fixtures.call_pickup(wazo_tenant=MAIN_TENANT) as main, fixtures.call_pickup(wazo_tenant=SUB_TENANT) as sub:
        response = confd.callpickups(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='CallPickup'))

        response = confd.callpickups(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()

