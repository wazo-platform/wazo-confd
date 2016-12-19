# -*- coding: utf-8 -*-

# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
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
from xivo_dao.resources.line_extension import dao as line_extension_dao
from xivo_dao.resources.parking_lot import dao as parking_lot_dao


from xivo_confd.helpers.validator import Validator, ValidationGroup, GetResource


class ExtenAvailableValidator(Validator):

    def __init__(self, dao, dao_parking_lot):
        self.dao = dao
        self.parking_lot_dao = dao_parking_lot

    def _validate_parking_lots(self, extension):
        if self._is_pattern(extension.exten):
            return

        parking_lots = self.parking_lot_dao.find_all_by()
        for parking_lot in parking_lots:
            if parking_lot.extensions and parking_lot.extensions[0].context == extension.context:
                if parking_lot.in_slots_range(extension.exten):
                    raise errors.resource_exists('ParkingLot',
                                                 id=parking_lot.id,
                                                 slots_start=parking_lot.slots_start,
                                                 slots_end=parking_lot.slots_end)

    def _is_pattern(self, exten):
        return exten.startswith('_')


class ExtenAvailableOnCreateValidator(ExtenAvailableValidator):

    def validate(self, extension):
        existing = self.dao.find_by(exten=extension.exten,
                                    context=extension.context)
        if existing:
            raise errors.resource_exists('Extension',
                                         exten=extension.exten,
                                         context=extension.context)

        self._validate_parking_lots(extension)


class ExtenAvailabelOnUpdateValidator(ExtenAvailableValidator):

    def validate(self, extension):
        existing = self.dao.find_by(exten=extension.exten,
                                    context=extension.context)
        if existing and existing.id != extension.id:
            raise errors.resource_exists('Extension',
                                         exten=extension.exten,
                                         context=extension.context)

        self._validate_parking_lots(extension)


class ContextOnUpdateValidator(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, extension):
        context = self.dao.get_by_name(extension.context)

        if extension.conference and context.type != 'internal':
            raise errors.unhandled_context_type(context.type)

        if extension.parking_lot and context.type != 'internal':
            raise errors.unhandled_context_type(context.type)

        if extension.group and context.type != 'internal':
            raise errors.unhandled_context_type(context.type)

        if extension.lines and context.type != 'internal':
            raise errors.unhandled_context_type(context.type)

        if extension.incall and context.type != 'incall':
            raise errors.unhandled_context_type(context.type)

        if extension.outcall and context.type != 'outcall':
            raise errors.unhandled_context_type(context.type)


class ExtensionRangeValidator(Validator):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, extension):
        if self._is_pattern(extension.exten):
            return

        context = self.dao.get_by_name(extension.context)
        if context.type == 'outcall':
            return

        context_ranges = (context.user_ranges +
                          context.group_ranges +
                          context.queue_ranges +
                          context.conference_room_ranges +
                          context.incall_ranges)
        if not self.extension_in_range(extension.exten, context_ranges):
            raise errors.outside_context_range(extension.exten, extension.context)

    def extension_in_range(self, exten, context_ranges):
        return any(context_range.in_range(exten)
                   for context_range in context_ranges)

    def _is_pattern(self, exten):
        return exten.startswith('_')


class ExtensionAssociationValidator(Validator):

    def __init__(self, dao, line_extension_dao):
        self.dao = dao
        self.line_extension_dao = line_extension_dao

    def validate(self, extension):
        extension_type, typeval = extension.type, extension.typeval

        # extensions that are created or dissociated are set to these values by default
        if extension_type != 'user' and typeval != '0':
            raise errors.resource_associated('Extension',
                                             extension_type,
                                             extension_id=extension.id,
                                             associated_id=typeval)

        line_extension = self.line_extension_dao.find_by_extension_id(extension.id)
        if line_extension:
            raise errors.resource_associated('Extension',
                                             'Line',
                                             extension_id=extension.id,
                                             line_id=line_extension.line_id)


def build_validator():
    return ValidationGroup(
        common=[
            GetResource('context', context_dao.get_by_name, 'Context'),
        ],
        create=[
            ExtenAvailableOnCreateValidator(extension_dao, parking_lot_dao),
            ExtensionRangeValidator(context_dao),
        ],
        edit=[
            ExtenAvailabelOnUpdateValidator(extension_dao, parking_lot_dao),
            ContextOnUpdateValidator(context_dao),
            ExtensionRangeValidator(context_dao),
        ],
        delete=[
            ExtensionAssociationValidator(extension_dao, line_extension_dao)
        ]
    )
