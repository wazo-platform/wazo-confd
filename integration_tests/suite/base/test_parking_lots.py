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
from ..helpers import errors as e, fixtures, scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT


def test_get_errors():
    fake_parking_lot = confd.parkinglots(999999).get
    yield s.check_resource_not_found, fake_parking_lot, 'ParkingLot'


def test_delete_errors():
    fake_parking_lot = confd.parkinglots(999999).delete
    yield s.check_resource_not_found, fake_parking_lot, 'ParkingLot'


def test_post_errors():
    url = confd.parkinglots.post
    for check in error_checks(url):
        yield check


@fixtures.parking_lot()
def test_put_errors(parking_lot):
    url = confd.parkinglots(parking_lot['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', 1234
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'slots_start', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'slots_start', '-1'
    yield s.check_bogus_field_returns_error, url, 'slots_start', True
    yield s.check_bogus_field_returns_error, url, 'slots_start', None
    yield s.check_bogus_field_returns_error, url, 'slots_start', []
    yield s.check_bogus_field_returns_error, url, 'slots_start', {}
    yield s.check_bogus_field_returns_error, url, 'slots_end', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'slots_end', '-1'
    yield s.check_bogus_field_returns_error, url, 'slots_end', True
    yield s.check_bogus_field_returns_error, url, 'slots_end', None
    yield s.check_bogus_field_returns_error, url, 'slots_end', []
    yield s.check_bogus_field_returns_error, url, 'slots_end', {}
    yield s.check_bogus_field_returns_error, url, 'timeout', 'string'
    yield s.check_bogus_field_returns_error, url, 'timeout', -1
    yield s.check_bogus_field_returns_error, url, 'timeout', []
    yield s.check_bogus_field_returns_error, url, 'timeout', {}
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', 1234
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', True
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', []
    yield s.check_bogus_field_returns_error, url, 'music_on_hold', {}


@fixtures.parking_lot(
    name='search',
    slots_start='701',
    slots_end='750',
    music_on_hold='search',
    timeout=100,
)
@fixtures.parking_lot(
    name='hidden',
    slots_start='801',
    slots_end='850',
    music_on_hold='hidden',
    timeout=None,
)
def test_search(parking_lot, hidden):
    url = confd.parkinglots
    searches = {
        'name': 'search',
        'slots_start': '701',
        'slots_end': '750',
        'music_on_hold': 'search',
        'timeout': 100,
    }

    for field, term in searches.items():
        yield check_search, url, parking_lot, hidden, field, term


def check_search(url, parking_lot, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, parking_lot[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: parking_lot[field]})
    assert_that(response.items, has_item(has_entry('id', parking_lot['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.parking_lot(name='sort1')
@fixtures.parking_lot(name='sort2')
def test_sorting_offset_limit(parking_lot1, parking_lot2):
    url = confd.parkinglots.get
    yield s.check_sorting, url, parking_lot1, parking_lot2, 'name', 'sort'

    yield s.check_offset, url, parking_lot1, parking_lot2, 'name', 'sort'
    yield s.check_offset_legacy, url, parking_lot1, parking_lot2, 'name', 'sort'

    yield s.check_limit, url, parking_lot1, parking_lot2, 'name', 'sort'


@fixtures.parking_lot(wazo_tenant=MAIN_TENANT)
@fixtures.parking_lot(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.parkinglots.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.parkinglots.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.parkinglots.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.parking_lot()
def test_get(parking_lot):
    response = confd.parkinglots(parking_lot['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=parking_lot['id'],
            name=parking_lot['name'],
            slots_start=parking_lot['slots_start'],
            slots_end=parking_lot['slots_end'],
            timeout=parking_lot['timeout'],
            music_on_hold=parking_lot['music_on_hold'],
            extensions=empty(),
        ),
    )


@fixtures.parking_lot(wazo_tenant=MAIN_TENANT)
@fixtures.parking_lot(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.parkinglots(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='ParkingLot'))

    response = confd.parkinglots(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.parkinglots.post(slots_start='701', slots_end='750')
    response.assert_created('parkinglots')

    assert_that(response.item, has_entries(id=not_(empty()), tenant_uuid=MAIN_TENANT))

    confd.parkinglots(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'MyParkingLot',
        'slots_start': '701',
        'slots_end': '750',
        'timeout': None,
        'music_on_hold': 'music',
    }

    response = confd.parkinglots.post(**parameters)
    response.assert_created('parkinglots')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.parkinglots(response.item['id']).delete().assert_deleted()


@fixtures.parking_lot()
def test_edit_minimal_parameters(parking_lot):
    response = confd.parkinglots(parking_lot['id']).put()
    response.assert_updated()


@fixtures.parking_lot()
def test_edit_all_parameters(parking_lot):
    parameters = {
        'name': 'MyParkingLot',
        'slots_start': '801',
        'slots_end': '850',
        'timeout': None,
        'music_on_hold': 'music',
    }

    response = confd.parkinglots(parking_lot['id']).put(**parameters)
    response.assert_updated()

    response = confd.parkinglots(parking_lot['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.parking_lot()
def test_edit_invalid_range(parking_lot):
    response = confd.parkinglots(parking_lot['id']).put(
        slots_start='700', slots_end='650'
    )
    response.assert_status(400)


@fixtures.parking_lot(wazo_tenant=MAIN_TENANT)
@fixtures.parking_lot(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.parkinglots(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='ParkingLot'))

    response = confd.parkinglots(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.parking_lot()
def test_delete(parking_lot):
    response = confd.parkinglots(parking_lot['id']).delete()
    response.assert_deleted()
    response = confd.parkinglots(parking_lot['id']).get()
    response.assert_match(404, e.not_found(resource='ParkingLot'))


@fixtures.parking_lot(wazo_tenant=MAIN_TENANT)
@fixtures.parking_lot(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.parkinglots(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='ParkingLot'))

    response = confd.parkinglots(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.parking_lot()
def test_bus_events(parking_lot):
    yield s.check_bus_event, 'config.parkinglots.created', confd.parkinglots.post, {
        'slots_start': '999',
        'slots_end': '999',
    }
    yield s.check_bus_event, 'config.parkinglots.edited', confd.parkinglots(
        parking_lot['id']
    ).put
    yield s.check_bus_event, 'config.parkinglots.deleted', confd.parkinglots(
        parking_lot['id']
    ).delete
