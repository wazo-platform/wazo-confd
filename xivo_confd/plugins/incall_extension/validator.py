# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from xivo_confd.helpers.validator import Validator, AssociationValidator


class IncallExtensionAssociationValidator(Validator):

    def validate(self, incall, extension):
        self.validate_incall_not_already_associated(incall)
        self.validate_extension_not_already_associated(extension)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_incall_context(extension)

    def validate_incall_not_already_associated(self, incall):
        extension = extension_dao.find_by(type='incall', typeval=str(incall.id))
        if extension:
            raise errors.resource_associated('Incall', 'Extension',
                                             incall_id=extension.typeval,
                                             extension_id=extension.id)

    def validate_extension_not_already_associated(self, extension):
        if extension.type == 'incall':
            raise errors.resource_associated('Incall', 'Extension',
                                             incall_id=extension.typeval,
                                             extension_id=extension.id)

    def validate_extension_not_associated_to_other_resource(self, extension):
        if not (extension.type == 'user' and extension.typeval == '0'):
            raise errors.resource_associated('Extension',
                                             extension.type,
                                             extension_id=extension.id,
                                             associated_id=extension.typeval)

    def validate_extension_is_in_incall_context(self, extension):
        context = context_dao.get_by_name(extension.context)
        if context.type != 'incall':
            raise errors.unhandled_context_type(context.type,
                                                extension.context,
                                                id=extension.id,
                                                context=extension.context)


class IncallExtensionDissociationValidator(Validator):

    def validate(self, incall, extension):
        self.validate_incall_extension_exists(incall, extension)

    def validate_incall_extension_exists(self, incall, extension):
        if not (extension.type == 'incall' and extension.typeval == str(incall.id)):
            raise errors.not_found('IncallExtension',
                                   incall_id=incall.id,
                                   extension_id=extension.id)


def build_validator():
    return AssociationValidator(
        association=[IncallExtensionAssociationValidator()],
        dissociation=[IncallExtensionDissociationValidator()]
    )
