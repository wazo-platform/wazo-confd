# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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

from xivo_confd.database import user_line as user_line_db
from xivo_confd.database import extension as extension_db

from xivo_confd.plugins.line_device.validator import ValidateLineHasNoDevice

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import Validator, AssociationValidator


class InternalAssociationValidator(Validator):

    def validate(self, line, extension):
        self.validate_line_has_endpoint(line)
        self.validate_line_has_no_extension(line)
        self.validate_extension_not_associated(extension)

    def validate_line_has_endpoint(self, line):
        if not line.is_associated():
            raise errors.missing_association('Line', 'Endpoint',
                                             line_id=line.id)

    def validate_line_has_no_extension(self, line):
        extension_id = user_line_db.find_extension_id_for_line(line.id)
        if extension_id:
            raise errors.resource_associated('Line', 'Extension',
                                             line_id=line.id,
                                             extension_id=extension_id)

    def validate_extension_not_associated(self, extension):
        resource, resource_id = extension_db.get_associated_resource(extension.id)
        if not (resource == 'user' and resource_id == '0'):
            raise errors.resource_associated('Extension',
                                             resource,
                                             id=extension.id,
                                             associated_id=resource_id)


class InternalDissociationValidator(Validator):

    def validate(self, line, extension):
        ValidateLineHasNoDevice().validate(line)


class IncallAssociationValidator(Validator):

    def validate(self, line, extension):
        self.validate_line_has_user(line)

    def validate_line_has_user(self, line):
        exists = user_line_db.check_line_has_users(line.id)
        if not exists:
            raise errors.missing_association('Line', 'User')


def build_internal_validator():
    return AssociationValidator(
        association=[InternalAssociationValidator()],
        dissociation=[InternalDissociationValidator()]
    )


def build_incall_validator():
    return AssociationValidator(
        association=[IncallAssociationValidator()]
    )
