# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
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
    fake_outcall = confd.outcalls(999999).get
    s.check_resource_not_found(fake_outcall, 'Outcall')


def test_delete_errors():
    fake_outcall = confd.outcalls(999999).delete
    s.check_resource_not_found(fake_outcall, 'Outcall')


def test_post_errors():
    url = confd.outcalls.post
    error_checks(url)


def test_put_errors():
    with fixtures.outcall() as outcall:
        url = confd.outcalls(outcall['id']).put
        error_checks(url)



def error_checks(url):
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', 123)
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', s.random_string(40))
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', [])
    s.check_bogus_field_returns_error(url, 'preprocess_subroutine', {})
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', None)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'name', 1234)
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'internal_caller_id', 1234)
    s.check_bogus_field_returns_error(url, 'internal_caller_id', 'invalid')
    s.check_bogus_field_returns_error(url, 'internal_caller_id', None)
    s.check_bogus_field_returns_error(url, 'internal_caller_id', [])
    s.check_bogus_field_returns_error(url, 'internal_caller_id', {})
    s.check_bogus_field_returns_error(url, 'ring_time', 'invalid')
    s.check_bogus_field_returns_error(url, 'ring_time', [])
    s.check_bogus_field_returns_error(url, 'ring_time', {})
    s.check_bogus_field_returns_error(url, 'description', 1234)
    s.check_bogus_field_returns_error(url, 'description', [])
    s.check_bogus_field_returns_error(url, 'description', {})
    s.check_bogus_field_returns_error(url, 'enabled', 'invalid')
    s.check_bogus_field_returns_error(url, 'enabled', None)
    s.check_bogus_field_returns_error(url, 'enabled', [])
    s.check_bogus_field_returns_error(url, 'enabled', {})

    unique_error_checks(url)


def unique_error_checks(url):
    with fixtures.outcall(name='unique') as outcall:
        s.check_bogus_field_returns_error(url, 'name', outcall['name'])



def test_search():
    with fixtures.outcall(description='search') as outcall, fixtures.outcall(description='hidden') as hidden:
        url = confd.outcalls
        searches = {'description': 'search'}

        for field, term in searches.items():
            check_search(url, outcall, hidden, field, term)



def check_search(url, outcall, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, outcall[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: outcall[field]})
    assert_that(response.items, has_item(has_entry('id', outcall['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def test_list_multi_tenant():
    with fixtures.outcall(wazo_tenant=MAIN_TENANT) as main, fixtures.outcall(wazo_tenant=SUB_TENANT) as sub:
        response = confd.outcalls.get(wazo_tenant=MAIN_TENANT)
        assert_that(
            response.items,
            all_of(has_item(main)), not_(has_item(sub)),
        )

        response = confd.outcalls.get(wazo_tenant=SUB_TENANT)
        assert_that(
            response.items,
            all_of(has_item(sub), not_(has_item(main))),
        )

        response = confd.outcalls.get(wazo_tenant=MAIN_TENANT, recurse=True)
        assert_that(
            response.items,
            has_items(main, sub),
        )



def test_sorting_offset_limit():
    with fixtures.outcall(description='sort1') as outcall1, fixtures.outcall(description='sort2') as outcall2:
        url = confd.outcalls.get
        s.check_sorting(url, outcall1, outcall2, 'description', 'sort')

        s.check_offset(url, outcall1, outcall2, 'description', 'sort')
        s.check_offset_legacy(url, outcall1, outcall2, 'description', 'sort')

        s.check_limit(url, outcall1, outcall2, 'description', 'sort')



def test_get():
    with fixtures.outcall() as outcall:
        response = confd.outcalls(outcall['id']).get()
        assert_that(
            response.item,
            has_entries(
                id=outcall['id'],
                tenant_uuid=MAIN_TENANT,
                preprocess_subroutine=outcall['preprocess_subroutine'],
                description=outcall['description'],
                internal_caller_id=outcall['internal_caller_id'],
                name=outcall['name'],
                ring_time=outcall['ring_time'],
                trunks=empty(),
            ))



def test_get_multi_tenant():
    with fixtures.outcall(wazo_tenant=MAIN_TENANT) as main, fixtures.outcall(wazo_tenant=SUB_TENANT) as sub:
        response = confd.outcalls(main['id']).get(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Outcall'))

        response = confd.outcalls(sub['id']).get(wazo_tenant=MAIN_TENANT)
        assert_that(response.item, has_entries(**sub))



def test_create_minimal_parameters():
    response = confd.outcalls.post(name='MyOutcall')
    response.assert_created('outcalls')

    assert_that(
        response.item,
        has_entries(
            id=not_(empty()),
            tenant_uuid=MAIN_TENANT,
        ))

    confd.outcalls(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {'name': 'MyOutcall',
                  'internal_caller_id': True,
                  'preprocess_subroutine': 'subroutine',
                  'ring_time': 10,
                  'description': 'outcall description',
                  'enabled': False}

    response = confd.outcalls.post(**parameters)
    response.assert_created('outcalls')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.outcalls(response.item['id']).delete().assert_deleted()


def test_edit_minimal_parameters():
    with fixtures.outcall() as outcall:
        response = confd.outcalls(outcall['id']).put()
        response.assert_updated()



def test_edit_all_parameters():
    with fixtures.outcall() as outcall:
        parameters = {'name': 'MyOutcall',
                      'internal_caller_id': True,
                      'preprocess_subroutine': 'subroutine',
                      'ring_time': 10,
                      'description': 'outcall description',
                      'enabled': False}

        response = confd.outcalls(outcall['id']).put(**parameters)
        response.assert_updated()

        response = confd.outcalls(outcall['id']).get()
        assert_that(response.item, has_entries(parameters))



def test_edit_multi_tenant():
    with fixtures.outcall(wazo_tenant=MAIN_TENANT) as main, fixtures.outcall(wazo_tenant=SUB_TENANT) as sub:
        response = confd.outcalls(main['id']).put(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Outcall'))

        response = confd.outcalls(sub['id']).put(wazo_tenant=MAIN_TENANT)
        response.assert_updated()



def test_delete():
    with fixtures.outcall() as outcall:
        response = confd.outcalls(outcall['id']).delete()
        response.assert_deleted()
        response = confd.outcalls(outcall['id']).get()
        response.assert_match(404, e.not_found(resource='Outcall'))



def test_delete_multi_tenant():
    with fixtures.outcall(wazo_tenant=MAIN_TENANT) as main, fixtures.outcall(wazo_tenant=SUB_TENANT) as sub:
        response = confd.outcalls(main['id']).delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found(resource='Outcall'))

        response = confd.outcalls(sub['id']).delete(wazo_tenant=MAIN_TENANT)
        response.assert_deleted()



def test_bus_events():
    with fixtures.outcall() as outcall:
        s.check_bus_event('config.outcalls.created', confd.outcalls.post, {'name': 'a'})
        s.check_bus_event('config.outcalls.edited', confd.outcalls(outcall['id']).put)
        s.check_bus_event('config.outcalls.deleted', confd.outcalls(outcall['id']).delete)

