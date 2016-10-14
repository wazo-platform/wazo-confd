# -*- coding: utf-8 -*-

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

from xivo_confd.helpers.validator import Validator, AssociationValidator


class OutcallExtensionAssociationValidator(Validator):

    def validate(self, outcall, extension):
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_outcall_context(extension)

    def validate_extension_not_associated_to_other_resource(self, extension):
        if not (extension.type == 'user' and extension.typeval == '0'):
            raise errors.resource_associated('Extension',
                                             extension.type,
                                             extension_id=extension.id,
                                             associated_id=extension.typeval)

    def validate_extension_is_in_outcall_context(self, extension):
        context = context_dao.get(extension.context)
        if context.type != 'outcall':
            raise errors.unhandled_context_type(context.type,
                                                extension.context,
                                                id=extension.id,
                                                context=extension.context)


class OutcallExtensionDissociationValidator(Validator):

    def validate(self, outcall, extension):
        self.validate_outcall_extension_exists(outcall, extension)

    def validate_outcall_extension_exists(self, outcall, extension):
        if extension not in outcall.extensions:
            raise errors.not_found('OutcallExtension',
                                   outcall_id=outcall.id,
                                   extension_id=extension.id)


def build_validator():
    return AssociationValidator(
        association=[OutcallExtensionAssociationValidator()],
        dissociation=[OutcallExtensionDissociationValidator()]
    )
