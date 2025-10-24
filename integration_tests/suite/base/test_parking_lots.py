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

from ..helpers import associations as a
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from ..helpers.config import CONTEXT, MAIN_TENANT, SUB_TENANT
from . import confd


def test_get_errors():
    fake_parking_lot = confd.parkinglots(999999).get
    s.check_resource_not_found(fake_parking_lot, 'ParkingLot')


def test_delete_errors():
    fake_parking_lot = confd.parkinglots(999999).delete
    s.check_resource_not_found(fake_parking_lot, 'ParkingLot')


def test_post_errors():
    url = confd.parkinglots
    error_checks(url.post)
    s.check_missing_body_returns_error(url, 'POST')


@fixtures.parking_lot()
def test_put_errors(parking_lot):
    url = confd.parkinglots(parking_lot['id'])
    error_checks(url.put)
    s.check_missing_body_returns_error(url, 'PUT')


def error_checks(url):
    s.check_bogus_field_returns_error(url, 'name', True)
    s.check_bogus_field_returns_error(url, 'name', 1234)
    s.check_bogus_field_returns_error(url, 'name', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'name', [])
    s.check_bogus_field_returns_error(url, 'name', {})
    s.check_bogus_field_returns_error(url, 'slots_start', 'invalid')
    s.check_bogus_field_returns_error(url, 'slots_start', '-1')
    s.check_bogus_field_returns_error(url, 'slots_start', True)
    s.check_bogus_field_returns_error(url, 'slots_start', None)
    s.check_bogus_field_returns_error(url, 'slots_start', [])
    s.check_bogus_field_returns_error(url, 'slots_start', {})
    s.check_bogus_field_returns_error(url, 'slots_end', 'invalid')
    s.check_bogus_field_returns_error(url, 'slots_end', '-1')
    s.check_bogus_field_returns_error(url, 'slots_end', True)
    s.check_bogus_field_returns_error(url, 'slots_end', None)
    s.check_bogus_field_returns_error(url, 'slots_end', [])
    s.check_bogus_field_returns_error(url, 'slots_end', {})
    s.check_bogus_field_returns_error(url, 'timeout', 'string')
    s.check_bogus_field_returns_error(url, 'timeout', -1)
    s.check_bogus_field_returns_error(url, 'timeout', [])
    s.check_bogus_field_returns_error(url, 'timeout', {})
    s.check_bogus_field_returns_error(url, 'music_on_hold', 1234)
    s.check_bogus_field_returns_error(url, 'music_on_hold', True)
    s.check_bogus_field_returns_error(url, 'music_on_hold', s.random_string(129))
    s.check_bogus_field_returns_error(url, 'music_on_hold', [])
    s.check_bogus_field_returns_error(url, 'music_on_hold', {})


@fixtures.extension(exten='700')
@fixtures.moh(label='search')
@fixtures.moh(label='hidden')
@fixtures.parking_lot(
    name='search',
    slots_start='701',
    slots_end='750',
    timeout=100,
)
@fixtures.parking_lot(
    name='hidden',
    slots_start='801',
    slots_end='850',
    timeout=None,
)
def test_search(extension, moh_visible, moh_hidden, parking_lot, hidden):
    parking_lot = confd.parkinglots(parking_lot['id']).get().item
    hidden = confd.parkinglots(hidden['id']).get().item

    url = confd.parkinglots
    searches = {
        'name': 'search',
        'slots_start': '701',
        'slots_end': '750',
        'timeout': 100,
    }

    for field, term in searches.items():
        check_search(url, parking_lot, hidden, field, term)

    searches = {'exten': extension['exten']}
    with a.parking_lot_extension(parking_lot, extension):
        for field, term in searches.items():
            check_relation_search(url, parking_lot, hidden, field, term)


def check_search(url, parking_lot, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, parking_lot[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: parking_lot[field]})
    assert_that(response.items, has_item(has_entry('id', parking_lot['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def check_relation_search(url, parking_lot, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry('id', parking_lot['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))

    response = url.get(**{field: term})
    assert_that(response.items, has_item(has_entry('id', parking_lot['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.parking_lot(name='sort1')
@fixtures.parking_lot(name='sort2')
def test_sorting_offset_limit(parking_lot1, parking_lot2):
    url = confd.parkinglots.get
    s.check_sorting(url, parking_lot1, parking_lot2, 'name', 'sort')

    s.check_offset(url, parking_lot1, parking_lot2, 'name', 'sort')
    s.check_limit(url, parking_lot1, parking_lot2, 'name', 'sort')


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


@fixtures.moh(label='music')
def test_create_all_parameters(moh):
    parameters = {
        'name': 'MyParkingLot',
        'slots_start': '701',
        'slots_end': '750',
        'timeout': None,
        'music_on_hold': moh['name'],
    }

    response = confd.parkinglots.post(**parameters)
    response.assert_created('parkinglots')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.parkinglots(response.item['id']).delete().assert_deleted()


@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_create_multitenant_moh(main_moh, sub_moh):
    parameters = {
        'name': 'MyParkingLot',
        'slots_start': '701',
        'slots_end': '750',
        'music_on_hold': main_moh['name'],
    }
    response = confd.parkinglots.post(**parameters)
    response.assert_created('parkinglots')
    confd.parkinglots(response.item['id']).delete().assert_deleted()

    response = confd.parkinglots.post(**parameters, wazo_tenant=SUB_TENANT)
    response.assert_match(400, e.not_found(resource='MOH'))

    parameters['music_on_hold'] = sub_moh['name']

    response = confd.parkinglots.post(**parameters, wazo_tenant=SUB_TENANT)
    response.assert_created('parkinglots')
    confd.parkinglots(response.item['id']).delete().assert_deleted()

    response = confd.parkinglots.post(**parameters)
    response.assert_match(400, e.not_found(resource='MOH'))


@fixtures.parking_lot()
def test_edit_minimal_parameters(parking_lot):
    response = confd.parkinglots(parking_lot['id']).put()
    response.assert_updated()


@fixtures.parking_lot()
@fixtures.moh(label='music')
def test_edit_all_parameters(parking_lot, moh):
    parameters = {
        'name': 'MyParkingLot',
        'slots_start': '801',
        'slots_end': '850',
        'timeout': None,
        'music_on_hold': moh['name'],
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


@fixtures.parking_lot(wazo_tenant=MAIN_TENANT)
@fixtures.parking_lot(wazo_tenant=SUB_TENANT)
@fixtures.moh(wazo_tenant=MAIN_TENANT)
@fixtures.moh(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant_moh(main, sub, main_moh, sub_moh):
    response = confd.parkinglots(main['id']).put(music_on_hold=sub_moh['name'])
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.parkinglots(sub['id']).put(music_on_hold=main_moh['name'])
    response.assert_match(400, e.not_found(resource='MOH'))

    response = confd.parkinglots(main['id']).put(music_on_hold=main_moh['name'])
    response.assert_updated()

    response = confd.parkinglots(sub['id']).put(music_on_hold=sub_moh['name'])
    response.assert_updated()


@fixtures.parking_lot(slots_start='1701', slots_end='1750')
@fixtures.extension(exten='1700')
@fixtures.extension(exten='1825')
def test_edit_range_when_other_extension_exists(
    parking_lot, parking_lot_extension, blocking_extension
):
    with a.parking_lot_extension(parking_lot, parking_lot_extension):
        parking_lot = dict(parking_lot)
        parking_lot['slots_start'] = '1801'
        parking_lot['slots_end'] = '1850'
        response = confd.parkinglots(parking_lot['id']).put(parking_lot)
        response.assert_status(400)


@fixtures.extension(exten='600', context=CONTEXT)
@fixtures.parking_lot(slots_start='601', slots_end='650')
@fixtures.extension(exten='400', context=CONTEXT)
@fixtures.parking_lot(slots_start='701', slots_end='750')
@fixtures.parking_lot(slots_start='801', slots_end='850', wazo_tenant=SUB_TENANT)
def test_edit_when_overlapping_slots(
    exten_edited_parking_lot,
    edited_parking_lot,
    exten_existing_parking_lot,
    existing_parking_lot,
    _,
):
    def assert_edition_fails(start, end):
        parking_lot = dict(edited_parking_lot)
        parking_lot['slots_start'] = start
        parking_lot['slots_end'] = end
        response = confd.parkinglots(parking_lot['id']).put(parking_lot)
        response.assert_match(400, e.extension_conflict())

    with (
        a.parking_lot_extension(existing_parking_lot, exten_existing_parking_lot),
        a.parking_lot_extension(edited_parking_lot, exten_edited_parking_lot),
    ):
        # same range
        assert_edition_fails('701', '750')
        # overlap end
        assert_edition_fails('750', '850')
        # overlap end -1
        assert_edition_fails('749', '850')
        # overlap start
        assert_edition_fails('601', '701')
        # overlap start +1
        assert_edition_fails('601', '702')
        # overlap inner
        assert_edition_fails('710', '711')
        # overlap outer
        assert_edition_fails('601', '850')

        # check there is no conflict with itself
        parking_lot = dict(edited_parking_lot)
        response = confd.parkinglots(edited_parking_lot['id']).put(parking_lot)
        response.assert_updated()

        # check there is no conflict with parking_lot from other tenant
        parking_lot = dict(edited_parking_lot)
        parking_lot['slots_start'] = '801'
        parking_lot['slots_end'] = '850'

        response = confd.parkinglots(edited_parking_lot['id']).put(parking_lot)
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
    url = confd.parkinglots(parking_lot['id'])
    headers = {'tenant_uuid': parking_lot['tenant_uuid']}

    response = s.check_event(
        'parking_lot_created',
        headers,
        confd.parkinglots.post,
        {
            'slots_start': '999',
            'slots_end': '999',
        },
    )
    confd.parkinglots(response.item['id']).delete().assert_deleted()

    s.check_event('parking_lot_edited', headers, url.put)
    s.check_event('parking_lot_deleted', headers, url.delete)
