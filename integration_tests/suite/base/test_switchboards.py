# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
)

from . import confd
from ..helpers import errors as e, fixtures, scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT

NOT_FOUND_SWITCHBOARD_UUID = 'uuid-not-found'


def test_get_errors():
    fake_switchboard = confd.switchboards(NOT_FOUND_SWITCHBOARD_UUID).get
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'


def test_delete_errors():
    fake_switchboard = confd.switchboards(NOT_FOUND_SWITCHBOARD_UUID).delete
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'


def test_post_errors():
    url = confd.switchboards.post
    for check in error_checks(url):
        yield check


@fixtures.switchboard()
def test_put_errors(switchboard):
    fake_switchboard = confd.switchboards(NOT_FOUND_SWITCHBOARD_UUID).put
    yield s.check_resource_not_found, fake_switchboard, 'Switchboard'

    url = confd.switchboards(switchboard['uuid']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}


@fixtures.switchboard(wazo_tenant=MAIN_TENANT)
@fixtures.switchboard(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.switchboards.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.switchboards.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.switchboards.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.switchboard(name='hidden', preprocess_subroutine='hidden')
@fixtures.switchboard(name='search', preprocess_subroutine='search')
def test_search(hidden, switchboard):
    url = confd.switchboards
    searches = {'name': 'search'}

    for field, term in searches.items():
        yield check_search, url, switchboard, hidden, field, term


def check_search(url, switchboard, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, switchboard[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: switchboard[field]})
    assert_that(response.items, has_item(has_entry('uuid', switchboard['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


@fixtures.switchboard(name='sort1')
@fixtures.switchboard(name='sort2')
def test_sorting(switchboard1, switchboard2):
    yield check_sorting, switchboard1, switchboard2, 'name', 'sort'


def check_sorting(switchboard1, switchboard2, field, search):
    response = confd.switchboards.get(search=search, order=field, direction='asc')
    assert_that(
        response.items,
        contains(
            has_entries(uuid=switchboard1['uuid']),
            has_entries(uuid=switchboard2['uuid']),
        ),
    )

    response = confd.switchboards.get(search=search, order=field, direction='desc')
    assert_that(
        response.items,
        contains(
            has_entries(uuid=switchboard2['uuid']),
            has_entries(uuid=switchboard1['uuid']),
        ),
    )


@fixtures.switchboard()
def test_get(switchboard):
    response = confd.switchboards(switchboard['uuid']).get()
    assert_that(
        response.item, has_entries(uuid=switchboard['uuid'], name=switchboard['name'])
    )


@fixtures.switchboard(wazo_tenant=MAIN_TENANT)
@fixtures.switchboard(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.switchboards(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Switchboard'))

    response = confd.switchboards(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.switchboards.post(name='MySwitchboard')
    response.assert_created('switchboards')

    assert_that(
        response.item,
        has_entries(uuid=not_(empty()), tenant_uuid=MAIN_TENANT, name='MySwitchboard'),
    )

    confd.switchboards(response.item['uuid']).delete().assert_deleted()


@fixtures.switchboard(name='before_edit')
def test_edit_minimal_parameters(switchboard):
    response = confd.switchboards(switchboard['uuid']).put(name='after_edit')
    response.assert_updated()

    response = confd.switchboards(switchboard['uuid']).get()
    assert_that(response.item, has_entries(name='after_edit'))


@fixtures.switchboard(wazo_tenant=MAIN_TENANT)
@fixtures.switchboard(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.switchboards(main['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Switchboard'))

    response = confd.switchboards(sub['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.switchboard()
def test_delete(switchboard):
    response = confd.switchboards(switchboard['uuid']).delete()
    response.assert_deleted()
    response = confd.switchboards(switchboard['uuid']).get()
    response.assert_match(404, e.not_found(resource='Switchboard'))


@fixtures.switchboard(wazo_tenant=MAIN_TENANT)
@fixtures.switchboard(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.switchboards(main['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Switchboard'))

    response = confd.switchboards(sub['uuid']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.switchboard()
def test_bus_events(switchboard):
    routing_key_create = 'config.switchboards.*.created'
    routing_key_edit = 'config.switchboards.{uuid}.edited'.format(
        uuid=switchboard['uuid']
    )
    routing_key_delete = 'config.switchboards.{uuid}.deleted'.format(
        uuid=switchboard['uuid']
    )

    yield s.check_bus_event, routing_key_create, confd.switchboards.post, {
        'name': 'bus_event'
    }
    yield s.check_bus_event, routing_key_edit, confd.switchboards(
        switchboard['uuid']
    ).put
    yield s.check_bus_event, routing_key_delete, confd.switchboards(
        switchboard['uuid']
    ).delete
