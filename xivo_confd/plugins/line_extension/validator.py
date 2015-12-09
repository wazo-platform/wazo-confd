# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from xivo_dao.helpers.db_manager import Session
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.extension import Extension

from xivo_confd.resources.line_device import validator as line_device_validator

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
        extension_id = (Session.query(UserLine.extension_id)
                        .filter(UserLine.line_id == line.id)
                        .filter(UserLine.extension_id != None)  # noqa
                        .scalar())

        if extension_id:
            raise errors.resource_associated('Line', 'Extension',
                                             line_id=line.id,
                                             extension_id=extension_id)

    def validate_extension_not_associated(self, extension):
        row = (Session.query(Extension.type.label('resource'),
                             Extension.typeval.label('resource_id'))
               .filter(Extension.id == extension.id)
               .first())

        if not (row.resource == 'user' and row.resource_id == '0'):
            raise errors.resource_associated('Extension',
                                             row.resource,
                                             id=extension.id,
                                             associated_id=row.resource_id)


class InternalDissociationValidator(Validator):

    def validate(self, line, extension):
        line_device_validator.validate_no_device(line.id)


class IncallAssociationValidator(Validator):

    def validate(self, line, extension):
        self.validate_line_has_user(line)

    def validate_line_has_user(self, line):
        query = (Session.query(UserLine)
                 .filter(UserLine.line_id == line.id)
                 .filter(UserLine.user_id != None)  # noqa
                 .exists())

        exists = Session.query(query).scalar()
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
