# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class ParkingLotExtensionAssociationValidator(ValidatorAssociation):

    def validate(self, parking_lot, extension):
        self.validate_parking_lot_not_already_associated(parking_lot)
        self.validate_extension_not_already_associated(extension)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_internal_context(extension)
        self.validate_extension_is_not_pattern(extension)
        self.validate_slots_do_not_conflict_with_extension_context(parking_lot, extension)

    def validate_parking_lot_not_already_associated(self, parking_lot):
        if parking_lot.extensions:
            raise errors.resource_associated('ParkingLot', 'Extension',
                                             parking_lot_id=parking_lot.id,
                                             extension_id=parking_lot.extensions[0].id)

    def validate_extension_not_already_associated(self, extension):
        if extension.parking_lot:
            raise errors.resource_associated('ParkingLot', 'Extension',
                                             parking_lot_id=extension.parking_lot.id,
                                             extension_id=extension.id)

    def validate_extension_not_associated_to_other_resource(self, extension):
        if not (extension.type == 'user' and extension.typeval == '0'):
            raise errors.resource_associated('Extension',
                                             extension.type,
                                             extension_id=extension.id,
                                             associated_id=extension.typeval)

    def validate_extension_is_in_internal_context(self, extension):
        context = context_dao.get_by_name(extension.context)
        if context.type != 'internal':
            raise errors.unhandled_context_type(context.type,
                                                extension.context,
                                                id=extension.id,
                                                context=extension.context)

    def validate_extension_is_not_pattern(self, extension):
        if extension.is_pattern():
            raise errors.invalid_exten_pattern(extension.exten)

    def validate_slots_do_not_conflict_with_extension_context(self, parking_lot, extension):
        extensions = extension_dao.find_all_by(context=extension.context)
        for extension in extensions:
            if extension.is_pattern():
                continue
            if parking_lot.in_slots_range(extension.exten):
                raise errors.resource_exists('Extension',
                                             id=extension.id,
                                             exten=extension.exten,
                                             context=extension.context)


class ParkingLotExtensionDissociationValidator(ValidatorAssociation):

    def validate(self, parking_lot, extension):
        self.validate_parking_lot_extension_exists(parking_lot, extension)

    def validate_parking_lot_extension_exists(self, parking_lot, extension):
        if extension.parking_lot != parking_lot:
            raise errors.not_found('ParkingLotExtension',
                                   parking_lot_id=parking_lot.id,
                                   extension_id=extension.id)


def build_validator():
    return ValidationAssociation(
        association=[ParkingLotExtensionAssociationValidator()],
        dissociation=[ParkingLotExtensionDissociationValidator()]
    )
