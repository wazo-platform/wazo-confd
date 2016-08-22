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

from xivo_confd.plugins.line_device.validator import ValidateLineHasNoDevice

from xivo_dao.helpers import errors
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd.helpers.validator import Validator, AssociationValidator


class InternalAssociationValidator(Validator):

    def validate(self, line, extension):
        self.validate_line_has_endpoint(line)
        self.validate_line_has_no_extension(line)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_line_has_no_different_user(line, extension)

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

    def validate_extension_not_associated_to_other_resource(self, extension):
        extension = extension_dao.find_by(id=extension.id)
        if extension.type != 'user':
            raise errors.resource_associated('Extension',
                                             extension.type,
                                             id=extension.id,
                                             associated_id=extension.typeval)

    def validate_line_has_no_different_user(self, line, extension):
        user_line = user_line_dao.find_by(line_id=line.id, main_user=True)
        if not user_line:
            return

        line_extensions = line_extension_dao.find_all_by(extension_id=extension.id)
        for line_extension in line_extensions:
            other_user_line = user_line_dao.find_by(line_id=line_extension.line_id, main_user=True)
            if not other_user_line:
                continue

            if other_user_line.user_id != user_line.user_id:
                raise errors.resource_associated('User', 'Line',
                                                 user_id=other_user_line.user_id,
                                                 line_id=other_user_line.line_id)


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
