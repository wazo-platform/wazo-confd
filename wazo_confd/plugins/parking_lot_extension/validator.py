# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.parking_lot import dao as parking_lot_dao

from wazo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class ParkingLotExtensionAssociationValidator(ValidatorAssociation):
    def validate(self, parking_lot, extension):
        self.validate_same_tenant(parking_lot, extension)
        self.validate_parking_lot_not_already_associated(parking_lot)
        self.validate_extension_not_already_associated(extension)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_internal_context(extension)
        self.validate_extension_is_not_pattern(extension)
        self.validate_slots_do_not_conflict_with_extension_context(
            parking_lot, extension
        )
        self.validate_slots_do_not_conflict_with_other_parking_slots(
            parking_lot, extension
        )

    def validate_same_tenant(self, parking_lot, extension):
        if extension.tenant_uuid != parking_lot.tenant_uuid:
            raise errors.different_tenants(
                extension_tenant_uuid=extension.tenant_uuid,
                parking_lot_tenant_uuid=parking_lot.tenant_uuid,
            )

    def validate_parking_lot_not_already_associated(self, parking_lot):
        if parking_lot.extensions:
            raise errors.resource_associated(
                'ParkingLot',
                'Extension',
                parking_lot_id=parking_lot.id,
                extension_id=parking_lot.extensions[0].id,
            )

    def validate_extension_not_already_associated(self, extension):
        if extension.parking_lot:
            raise errors.resource_associated(
                'ParkingLot',
                'Extension',
                parking_lot_id=extension.parking_lot.id,
                extension_id=extension.id,
            )

    def validate_extension_not_associated_to_other_resource(self, extension):
        if not (extension.type == 'user' and extension.typeval == '0'):
            raise errors.resource_associated(
                'Extension',
                extension.type,
                extension_id=extension.id,
                associated_id=extension.typeval,
            )

    def validate_extension_is_in_internal_context(self, extension):
        context = context_dao.get_by_name(extension.context)
        if context.type != 'internal':
            raise errors.unhandled_context_type(
                context.type,
                extension.context,
                id=extension.id,
                context=extension.context,
            )

    def validate_extension_is_not_pattern(self, extension):
        if extension.is_pattern():
            raise errors.invalid_exten_pattern(extension.exten)

    def validate_slots_do_not_conflict_with_extension_context(
        self, parking_lot, extension
    ):
        extensions = extension_dao.find_all_by(context=extension.context)
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

    def validate_slots_do_not_conflict_with_other_parking_slots(
        self, parking_lot, extension
    ):
        sibling_parking_lots = parking_lot_dao.find_all_by(context=extension.context)
        for sibling_parking_lot in sibling_parking_lots:
            if sibling_parking_lot.in_slots_range(parking_lot.slots_start):
                raise errors.extension_conflict(
                    'Extension',
                    exten=parking_lot.slots_start,
                    context=extension.context,
                    parking_lot_id=sibling_parking_lot.id,
                )
            if sibling_parking_lot.in_slots_range(parking_lot.slots_end):
                raise errors.extension_conflict(
                    'Extension',
                    exten=parking_lot.slots_end,
                    context=extension.context,
                    parking_lot_id=sibling_parking_lot.id,
                )
            if parking_lot.in_slots_range(sibling_parking_lot.slots_start):
                raise errors.extension_conflict(
                    'Extension',
                    exten=sibling_parking_lot.slots_start,
                    context=extension.context,
                    parking_lot_id=sibling_parking_lot.id,
                )
            if parking_lot.in_slots_range(sibling_parking_lot.slots_end):
                raise errors.extension_conflict(
                    'Extension',
                    exten=sibling_parking_lot.slots_end,
                    context=extension.context,
                    parking_lot_id=sibling_parking_lot.id,
                )


def build_validator():
    return ValidationAssociation(
        association=[ParkingLotExtensionAssociationValidator()]
    )
