# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_confd.helpers.validator import AssociationValidator
from xivo_confd.helpers.validator import Validator

from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao

from xivo_dao.helpers import errors


class ValidateLineAssociation(Validator):

    def validate(self, line, endpoint):
        if line.is_associated():
            raise errors.resource_associated('Line', 'Endpoint',
                                             line_id=line.id,
                                             endpoint=line.endpoint,
                                             endpoint_id=line.endpoint_id)


class ValidateLineDissociation(Validator):

    def __init__(self, user_line_dao, line_extension_dao):
        self.user_line_dao = user_line_dao
        self.line_extension_dao = line_extension_dao

    def validate(self, line, endpoint):
        self.validate_endpoint(line, endpoint)
        self.validate_users(line)
        self.validate_extensions(line)

    def validate_endpoint(self, line, endpoint):
        if not line.is_associated_with(endpoint):
            raise errors.resource_not_associated('Line', 'Endpoint',
                                                 line_id=line.id,
                                                 endpoint_id=endpoint.id)

    def validate_users(self, line):
        user_lines = self.user_line_dao.find_all_by_line_id(line.id)
        if user_lines:
            user_ids = ','.join(str(ul.user_id) for ul in user_lines)
            raise errors.resource_associated('Line', 'User',
                                             line_id=line.id,
                                             user_ids=user_ids)

    def validate_extensions(self, line):
        line_extensions = self.line_extension_dao.find_all_by_line_id(line.id)
        if line_extensions:
            extension_ids = ','.join(str(le.extension_id) for le in line_extensions)
            raise errors.resource_associated('Line', 'Extension',
                                             line_id=line.id,
                                             extension_ids=extension_ids)


def build_validator():
    return AssociationValidator(
        association=[
            ValidateLineAssociation(),
        ],
        dissociation=[
            ValidateLineDissociation(user_line_dao,
                                     line_extension_dao)
        ]
    )
