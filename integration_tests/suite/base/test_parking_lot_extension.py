# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (assert_that,
                      contains,
                      has_entries)
from ..helpers import scenarios as s
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import associations as a
from xivo_test_helpers.confd.config import INCALL_CONTEXT, CONTEXT
from . import confd


FAKE_ID = 999999999


@fixtures.parking_lot()
@fixtures.extension()
def test_associate_errors(parking_lot, extension):
    fake_parking_lot = confd.parkinglots(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.parkinglots(parking_lot['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_parking_lot, 'ParkingLot'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.parking_lot()
@fixtures.extension()
def test_dissociate_errors(parking_lot, extension):
    fake_parking_lot_extension = confd.parkinglots(parking_lot['id']).extensions(extension['id']).delete
    fake_parking_lot = confd.parkinglots(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.parkinglots(parking_lot['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_parking_lot, 'ParkingLot'
    yield s.check_resource_not_found, fake_extension, 'Extension'
    yield s.check_resource_not_found, fake_parking_lot_extension, 'ParkingLotExtension'


@fixtures.parking_lot()
@fixtures.extension()
def test_associate(parking_lot, extension):
    response = confd.parkinglots(parking_lot['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.parking_lot()
@fixtures.extension()
def test_associate_already_associated(parking_lot, extension):
    with a.parking_lot_extension(parking_lot, extension):
        response = confd.parkinglots(parking_lot['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('ParkingLot', 'Extension'))


@fixtures.parking_lot()
@fixtures.extension()
@fixtures.extension()
def test_associate_multiple_extensions_to_parking_lot(parking_lot, extension1, extension2):
    with a.parking_lot_extension(parking_lot, extension1):
        response = confd.parkinglots(parking_lot['id']).extensions(extension2['id']).put()
        response.assert_match(400, e.resource_associated('ParkingLot', 'Extension'))


@fixtures.parking_lot()
@fixtures.parking_lot()
@fixtures.extension()
def test_associate_multiple_parking_lots_to_extension(parking_lot1, parking_lot2, extension):
    with a.parking_lot_extension(parking_lot1, extension):
        response = confd.parkinglots(parking_lot2['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('ParkingLot', 'Extension'))


@fixtures.parking_lot()
@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_when_user_already_associated(parking_lot, user, line_sip, extension):
    with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
        response = confd.parkinglots(parking_lot['id']).extensions(extension['id']).put()
        response.assert_match(400, e.resource_associated('user', 'Extension'))


@fixtures.parking_lot()
@fixtures.extension(context=INCALL_CONTEXT)
def test_associate_when_not_internal_context(parking_lot, extension):
    response = confd.parkinglots(parking_lot['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.parking_lot(slots_start='1701', slots_end='1750')
@fixtures.extension(exten='1725')
def test_associate_when_in_slots_range(parking_lot, extension):
    response = confd.parkinglots(parking_lot['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.parking_lot(slots_start='1701', slots_end='1750')
@fixtures.extension(exten='1700')
@fixtures.extension(exten='1725')
def test_associate_when_other_extension_exists(parking_lot, extension1, extension2):
    response = confd.parkinglots(parking_lot['id']).extensions(extension1['id']).put()
    response.assert_status(400)


@fixtures.parking_lot(slots_start='1701', slots_end='1750')
@fixtures.extension(exten='_XXXX')
def test_associate_when_exten_is_pattern(parking_lot, extension):
    response = confd.parkinglots(parking_lot['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.parking_lot()
@fixtures.extension()
def test_dissociate(parking_lot, extension):
    with a.parking_lot_extension(parking_lot, extension, check=False):
        response = confd.parkinglots(parking_lot['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.parking_lot()
@fixtures.extension()
def test_get_parking_lot_relation(parking_lot, extension):
    with a.parking_lot_extension(parking_lot, extension):
        response = confd.parkinglots(parking_lot['id']).get()
        assert_that(response.item, has_entries(
            extensions=contains(has_entries(id=extension['id'],
                                            exten=extension['exten'],
                                            context=extension['context']))
        ))


@fixtures.extension()
@fixtures.parking_lot()
def test_get_extension_relation(extension, parking_lot):
    with a.parking_lot_extension(parking_lot, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(response.item, has_entries(
            parking_lot=has_entries(id=parking_lot['id'],
                                    name=parking_lot['name'])
        ))


@fixtures.parking_lot()
@fixtures.extension()
def test_edit_context_to_parking_lot_when_associated(parking_lot, extension):
    with a.parking_lot_extension(parking_lot, extension):
        response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
        response.assert_status(400)


@fixtures.parking_lot(slots_start='1701', slots_end='1750')
@fixtures.extension(exten='1700')
def test_create_exten_in_parking_lot_range(parking_lot, extension):
    with a.parking_lot_extension(parking_lot, extension):
        response = confd.extensions().post(exten='1725', context=CONTEXT)
        response.assert_status(400)


@fixtures.parking_lot(slots_start='1701', slots_end='1750')
@fixtures.extension(exten='1700')
@fixtures.extension()
def test_edit_exten_in_parking_lot_range(parking_lot, extension1, extension2):
    with a.parking_lot_extension(parking_lot, extension1):
        response = confd.extensions(extension2['id']).put(exten='1725')
        response.assert_status(400)


@fixtures.parking_lot(slots_start='1701', slots_end='1750')
@fixtures.extension(exten='1700', context=CONTEXT)
@fixtures.extension(context=INCALL_CONTEXT)
def test_edit_exten_in_parking_lot_range_when_different_context(parking_lot, extension1, extension2):
    with a.parking_lot_extension(parking_lot, extension1):
        response = confd.extensions(extension2['id']).put(exten='1725')
        response.assert_updated()


@fixtures.parking_lot(slots_start='1701', slots_end='1750')
@fixtures.extension(exten='1700')
@fixtures.extension(exten='1825')
def test_edit_slots_when_other_exten_exists(parking_lot, extension, _):
    with a.parking_lot_extension(parking_lot, extension):
        response = confd.parkinglots(parking_lot['id']).put(slots_start='1801', slots_end='1850')
        response.assert_status(400)


@fixtures.parking_lot(slots_start='1701', slots_end='1750')
@fixtures.extension(exten='1700')
@fixtures.extension(exten='_182X')
def test_edit_slots_when_other_exten_exists_and_is_pattern(parking_lot, extension, _):
    with a.parking_lot_extension(parking_lot, extension):
        response = confd.parkinglots(parking_lot['id']).put(slots_start='1801', slots_end='1850')
        response.assert_updated()


@fixtures.parking_lot()
@fixtures.extension()
def test_delete_parking_lot_when_parking_lot_and_extension_associated(parking_lot, extension):
    with a.parking_lot_extension(parking_lot, extension, check=False):
        response = confd.parkinglots(parking_lot['id']).delete()
        response.assert_deleted()


def test_delete_extension_when_parking_lot_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
