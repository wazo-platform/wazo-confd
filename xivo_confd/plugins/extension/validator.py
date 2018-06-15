# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import re

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import (
    InputError,
    NotFoundError,
)
from xivo_dao.resources.context import dao as context_dao_module
from xivo_dao.resources.extension import dao as extension_dao_module
from xivo_dao.resources.line_extension import dao as line_extension_dao_module
from xivo_dao.resources.parking_lot import dao as parking_lot_dao_module


from xivo_confd.helpers.validator import (
    EXTEN_REGEX,
    EXTEN_OUTCALL_REGEX,
    BaseExtensionRangeMixin,
    GetResource,
    ValidationGroup,
    Validator,
)


class ExtenAvailableValidator(Validator):

    def __init__(self, dao, dao_parking_lot):
        self.dao = dao
        self.parking_lot_dao = dao_parking_lot

    def _validate_parking_lots(self, extension):
        if extension.is_pattern():
            return

        parking_lots = self.parking_lot_dao.find_all_by()
        for parking_lot in parking_lots:
            if parking_lot.extensions and parking_lot.extensions[0].context == extension.context:
                if parking_lot.in_slots_range(extension.exten):
                    raise errors.resource_exists('ParkingLot',
                                                 id=parking_lot.id,
                                                 slots_start=parking_lot.slots_start,
                                                 slots_end=parking_lot.slots_end)


class ExtenAvailableOnCreateValidator(ExtenAvailableValidator):

    def validate(self, extension):
        existing = self.dao.find_by(exten=extension.exten,
                                    context=extension.context)
        if existing:
            raise errors.resource_exists('Extension',
                                         exten=extension.exten,
                                         context=extension.context)

        self._validate_parking_lots(extension)


class ExtenAvailableOnUpdateValidator(ExtenAvailableValidator):

    def validate(self, extension):
        existing = self.dao.find_by(exten=extension.exten,
                                    context=extension.context)
        if existing and existing.id != extension.id:
            raise errors.resource_exists('Extension',
                                         exten=extension.exten,
                                         context=extension.context)

        self._validate_parking_lots(extension)


class ExtenRegexValidator(Validator):

    exten_regex = re.compile(EXTEN_REGEX)
    exten_outcall_regex = re.compile(EXTEN_OUTCALL_REGEX)

    def __init__(self, context_dao):
        self._context_dao = context_dao

    def validate(self, extension):
        context = self._context_dao.get_by_name(extension.context)

        if context.type == 'outcall':
            self._validate_regexp(self.exten_outcall_regex, extension.exten)
        else:
            self._validate_regexp(self.exten_regex, extension.exten)

    def _validate_regexp(self, regexp, value):
        if regexp.match(value) is None:
            raise InputError("exten: ['String does not match expected pattern.']")


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

        if extension.queue and context.type != 'internal':
            raise errors.unhandled_context_type(context.type)


class ContextExistsValidator(Validator):

    def __init__(self, context_dao):
        self.context_dao = context_dao

    def validate(self, extension, tenant_uuids):
        try:
            self.context_dao.get_by(name=extension.context, tenant_uuids=tenant_uuids)
        except NotFoundError:
            metadata = {'context': extension.context}
            raise errors.param_not_found('context', 'Context', **metadata)


class ExtensionRangeValidator(Validator, BaseExtensionRangeMixin):

    def __init__(self, dao):
        self.dao = dao

    def validate(self, extension):
        if self._is_pattern(extension.exten):
            return

        context = self.dao.get_by_name(extension.context)

        if extension.conference and not self._exten_in_range(extension.exten, context.conference_room_ranges):
            raise errors.outside_context_range(extension.exten, extension.context)

        if extension.group and not self._exten_in_range(extension.exten, context.group_ranges):
            raise errors.outside_context_range(extension.exten, extension.context)

        if extension.incall and not self._exten_in_range(extension.exten, context.incall_ranges):
            raise errors.outside_context_range(extension.exten, extension.context)

        if extension.lines and not self._exten_in_range(extension.exten, context.user_ranges):
            raise errors.outside_context_range(extension.exten, extension.context)

        if extension.queue and not self._exten_in_range(extension.exten, context.queue_ranges):
            raise errors.outside_context_range(extension.exten, extension.context)


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


def build_context_exists_validator():
    return ContextExistsValidator(context_dao_module)


def build_validator():
    return ValidationGroup(
        common=[
            GetResource('context', context_dao_module.get_by_name, 'Context'),
        ],
        create=[
            ExtenAvailableOnCreateValidator(extension_dao_module, parking_lot_dao_module),
            ExtenRegexValidator(context_dao_module),
        ],
        edit=[
            ExtenAvailableOnUpdateValidator(extension_dao_module, parking_lot_dao_module),
            ContextOnUpdateValidator(context_dao_module),
            ExtensionRangeValidator(context_dao_module),
            ExtenRegexValidator(context_dao_module),
        ],
        delete=[
            ExtensionAssociationValidator(extension_dao_module, line_extension_dao_module)
        ]
    )
