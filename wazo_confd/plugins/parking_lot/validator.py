# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.moh import dao as moh_dao
from xivo_dao.resources.parking_lot import dao as parking_lot_dao

from wazo_confd.helpers.validator import MOHExists, ValidationGroup, Validator


class SlotsAvailableValidator(Validator):
    def validate(self, parking_lot):
        self.validate_slots_do_not_conflict_with_extension_context(parking_lot)
        self.validate_slots_do_not_conflict_with_other_parking_slots(parking_lot)

    def validate_slots_do_not_conflict_with_extension_context(self, parking_lot):
        if not parking_lot.extensions:
            return

        parking_lot_context = parking_lot.extensions[0].context
        extensions = extension_dao.find_all_by(context=parking_lot_context)
        for extension in extensions:
            if extension.is_pattern():
                continue
            if parking_lot.in_slots_range(extension.exten):
                raise errors.resource_exists(
                    'Extension',
                    id=extension.id,
                    exten=extension.exten,
                    context=extension.context,
                )

    def validate_slots_do_not_conflict_with_other_parking_slots(self, parking_lot):
        if not parking_lot.extensions:
            return

        parking_lot_context = parking_lot.extensions[0].context
        sibling_parking_lots = (
            sibling_parking_lot
            for sibling_parking_lot in parking_lot_dao.find_all_by(
                context=parking_lot_context
            )
            if sibling_parking_lot.id != parking_lot.id
        )
        for sibling_parking_lot in sibling_parking_lots:
            if sibling_parking_lot.in_slots_range(parking_lot.slots_start):
                raise errors.extension_conflict(
                    'Extension',
                    exten=parking_lot.slots_start,
                    context=parking_lot_context,
                    parking_lot_id=sibling_parking_lot.id,
                )
            if sibling_parking_lot.in_slots_range(parking_lot.slots_end):
                raise errors.extension_conflict(
                    'Extension',
                    exten=parking_lot.slots_end,
                    context=parking_lot_context,
                    parking_lot_id=sibling_parking_lot.id,
                )
            if parking_lot.in_slots_range(sibling_parking_lot.slots_start):
                raise errors.extension_conflict(
                    'Extension',
                    exten=sibling_parking_lot.slots_start,
                    context=parking_lot_context,
                    parking_lot_id=sibling_parking_lot.id,
                )
            if parking_lot.in_slots_range(sibling_parking_lot.slots_end):
                raise errors.extension_conflict(
                    'Extension',
                    exten=sibling_parking_lot.slots_end,
                    context=parking_lot_context,
                    parking_lot_id=sibling_parking_lot.id,
                )


def build_validator():
    moh_validator = MOHExists('music_on_hold', moh_dao.get_by)
    return ValidationGroup(
        create=[moh_validator],
        edit=[SlotsAvailableValidator(), moh_validator],
    )
