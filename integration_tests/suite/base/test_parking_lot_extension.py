# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains, has_entries

from . import confd
from ..helpers import associations as a, errors as e, fixtures, scenarios as s
from ..helpers.config import CONTEXT, INCALL_CONTEXT, MAIN_TENANT, SUB_TENANT

FAKE_ID = 999999999


@fixtures.parking_lot()
@fixtures.extension()
def test_associate_errors(parking_lot, extension):
    fake_parking_lot = confd.parkinglots(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.parkinglots(parking_lot['id']).extensions(FAKE_ID).put

    s.check_resource_not_found(fake_parking_lot, 'ParkingLot')
    s.check_resource_not_found(fake_extension, 'Extension')


@fixtures.parking_lot()
@fixtures.extension()
def test_dissociate_errors(parking_lot, extension):
    fake_parking_lot = confd.parkinglots(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.parkinglots(parking_lot['id']).extensions(FAKE_ID).delete

    s.check_resource_not_found(fake_parking_lot, 'ParkingLot')
    s.check_resource_not_found(fake_extension, 'Extension')


@fixtures.parking_lot()
@fixtures.extension()
def test_associate(parking_lot, extension):
    response = confd.parkinglots(parking_lot['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.parking_lot()
@fixtures.extension()
def test_associate_already_associated(parking_lot, extension):
    with a.parking_lot_extension(parking_lot, extension):
        response = (
            confd.parkinglots(parking_lot['id']).extensions(extension['id']).put()
        )
        response.assert_updated()


@fixtures.parking_lot()
@fixtures.extension()
@fixtures.extension()
def test_associate_multiple_extensions_to_parking_lot(
    parking_lot, extension1, extension2
):
    with a.parking_lot_extension(parking_lot, extension1):
        response = (
            confd.parkinglots(parking_lot['id']).extensions(extension2['id']).put()
        )
        response.assert_match(400, e.resource_associated('ParkingLot', 'Extension'))


@fixtures.parking_lot()
@fixtures.parking_lot()
@fixtures.extension()
def test_associate_multiple_parking_lots_to_extension(
    parking_lot1, parking_lot2, extension
):
    with a.parking_lot_extension(parking_lot1, extension):
        response = (
            confd.parkinglots(parking_lot2['id']).extensions(extension['id']).put()
        )
        response.assert_match(400, e.resource_associated('ParkingLot', 'Extension'))


@fixtures.parking_lot()
@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
def test_associate_when_user_already_associated(parking_lot, user, line_sip, extension):
    with a.user_line(user, line_sip), a.line_extension(line_sip, extension):
        response = (
            confd.parkinglots(parking_lot['id']).extensions(extension['id']).put()
        )
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


@fixtures.extension(exten='600', context=CONTEXT)
@fixtures.extension(exten='400', context=CONTEXT)
@fixtures.parking_lot(slots_start='701', slots_end='750')
@fixtures.parking_lot(slots_start='801', slots_end='850', wazo_tenant=SUB_TENANT)
def test_associate_when_overlapping_slots(
    exten_new_parking, exten_existing_parking, existing_parking, _
):
    def assert_association_fails(start, end):
        with fixtures.parking_lot(slots_start=start, slots_end=end) as parking_lot:
            response = (
                confd.parkinglots(parking_lot['id'])
                .extensions(exten_new_parking['id'])
                .put()
            )
            response.assert_match(400, e.extension_conflict())

    with a.parking_lot_extension(existing_parking, exten_existing_parking):
        # same range
        assert_association_fails('701', '750')
        # overlap end
        assert_association_fails('750', '850')
        # overlap end -1
        assert_association_fails('749', '850')
        # overlap start
        assert_association_fails('601', '701')
        # overlap start +1
        assert_association_fails('601', '702')
        # overlap inner
        assert_association_fails('710', '711')
        # overlap outer
        assert_association_fails('601', '850')

        # check there is no conflict with parking_lot from other tenant
        parameters = {
            'slots_start': '801',
            'slots_end': '850',
        }

        response = confd.parkinglots.post(**parameters)
        response.assert_created('parkinglots')
        confd.parkinglots(response.item['id']).delete().assert_deleted()


@fixtures.context(wazo_tenant=MAIN_TENANT, label='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, label='sub-internal')
@fixtures.parking_lot(wazo_tenant=MAIN_TENANT)
@fixtures.parking_lot(wazo_tenant=SUB_TENANT)
def test_associate_multi_tenant(main_ctx, sub_ctx, main_pl, sub_pl):
    with fixtures.extension(context=main_ctx['name']) as main_extension:
        with fixtures.extension(context=sub_ctx['name']) as sub_extension:
            response = (
                confd.parkinglots(sub_pl['id'])
                .extensions(main_extension['id'])
                .put(wazo_tenant=SUB_TENANT)
            )
            response.assert_match(404, e.not_found('Extension'))

            response = (
                confd.parkinglots(main_pl['id'])
                .extensions(sub_extension['id'])
                .put(wazo_tenant=SUB_TENANT)
            )
            response.assert_match(404, e.not_found('ParkingLot'))

            response = (
                confd.parkinglots(main_pl['id'])
                .extensions(sub_extension['id'])
                .put(wazo_tenant=MAIN_TENANT)
            )
            response.assert_match(400, e.different_tenant())


@fixtures.parking_lot()
@fixtures.extension()
def test_dissociate(parking_lot, extension):
    with a.parking_lot_extension(parking_lot, extension, check=False):
        response = (
            confd.parkinglots(parking_lot['id']).extensions(extension['id']).delete()
        )
        response.assert_deleted()


@fixtures.parking_lot()
@fixtures.extension()
def test_dissociate_not_associated(parking_lot, extension):
    response = confd.parkinglots(parking_lot['id']).extensions(extension['id']).delete()
    response.assert_deleted()


@fixtures.context(wazo_tenant=MAIN_TENANT, label='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, label='sub-internal')
@fixtures.parking_lot(wazo_tenant=MAIN_TENANT)
@fixtures.parking_lot(wazo_tenant=SUB_TENANT)
def test_dissociate_multi_tenant(main_ctx, sub_ctx, main_pl, sub_pl):
    with fixtures.extension(context=main_ctx['name']) as main_extension:
        with fixtures.extension(context=sub_ctx['name']) as sub_extension:
            response = (
                confd.parkinglots(sub_pl['id'])
                .extensions(main_extension['id'])
                .delete(wazo_tenant=SUB_TENANT)
            )
            response.assert_match(404, e.not_found('Extension'))

            response = (
                confd.parkinglots(main_pl['id'])
                .extensions(sub_extension['id'])
                .delete(wazo_tenant=SUB_TENANT)
            )
            response.assert_match(404, e.not_found('ParkingLot'))


@fixtures.parking_lot()
@fixtures.extension()
def test_get_parking_lot_relation(parking_lot, extension):
    with a.parking_lot_extension(parking_lot, extension):
        response = confd.parkinglots(parking_lot['id']).get()
        assert_that(
            response.item,
            has_entries(
                extensions=contains(
                    has_entries(
                        id=extension['id'],
                        exten=extension['exten'],
                        context=extension['context'],
                    )
                )
            ),
        )


@fixtures.extension()
@fixtures.parking_lot()
def test_get_extension_relation(extension, parking_lot):
    with a.parking_lot_extension(parking_lot, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(
            response.item,
            has_entries(
                parking_lot=has_entries(id=parking_lot['id'], name=parking_lot['name'])
            ),
        )


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
def test_edit_exten_in_parking_lot_range_when_different_context(
    parking_lot, extension1, extension2
):
    with a.parking_lot_extension(parking_lot, extension1):
        response = confd.extensions(extension2['id']).put(exten='1725')
        response.assert_updated()


@fixtures.parking_lot(slots_start='1701', slots_end='1750')
@fixtures.extension(exten='1700')
@fixtures.extension(exten='1825')
def test_edit_slots_when_other_exten_exists(parking_lot, extension, _):
    with a.parking_lot_extension(parking_lot, extension):
        response = confd.parkinglots(parking_lot['id']).put(
            slots_start='1801', slots_end='1850'
        )
        response.assert_status(400)


@fixtures.parking_lot(slots_start='1701', slots_end='1750')
@fixtures.extension(exten='1700')
@fixtures.extension(exten='_182X')
def test_edit_slots_when_other_exten_exists_and_is_pattern(parking_lot, extension, _):
    with a.parking_lot_extension(parking_lot, extension):
        response = confd.parkinglots(parking_lot['id']).put(
            slots_start='1801', slots_end='1850'
        )
        response.assert_updated()


@fixtures.parking_lot()
@fixtures.extension()
def test_delete_parking_lot_when_parking_lot_and_extension_associated(
    parking_lot, extension
):
    with a.parking_lot_extension(parking_lot, extension, check=False):
        response = confd.parkinglots(parking_lot['id']).delete()
        response.assert_deleted()


def test_delete_extension_when_parking_lot_and_extension_associated():
    # It is impossible to delete an extension while it associated to an object
    pass
