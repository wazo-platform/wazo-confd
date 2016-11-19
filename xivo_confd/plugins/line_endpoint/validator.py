# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from xivo_confd.helpers.validator import ValidationAssociation
from xivo_confd.helpers.validator import Validator

from xivo_confd.plugins.line_device.validator import ValidateLineHasNoDevice

from xivo_dao.resources.user_line import dao as user_line_dao_module
from xivo_dao.resources.line_extension import dao as line_extension_dao_module
from xivo_dao.resources.line import dao as line_dao_module
from xivo_dao.resources.trunk import dao as trunk_dao_module

from xivo_dao.helpers import errors


class ValidateLineAssociation(Validator):

    def __init__(self, endpoint, line_dao, trunk_dao):
        super(ValidateLineAssociation, self).__init__()
        self.endpoint = endpoint
        self.line_dao = line_dao
        self.trunk_dao = trunk_dao

    def validate(self, line, endpoint):
        self.validate_not_already_associated(line, endpoint)
        self.validate_not_associated_to_line(line, endpoint)
        self.validate_not_associated_to_trunk(line, endpoint)

    def validate_not_already_associated(self, line, endpoint):
        if line.is_associated():
            raise errors.resource_associated('Line', 'Endpoint',
                                             line_id=line.id,
                                             endpoint=line.endpoint,
                                             endpoint_id=line.endpoint_id)

    def validate_not_associated_to_line(self, line, endpoint):
        line = self.line_dao.find_by(endpoint=self.endpoint, endpoint_id=endpoint.id)
        if line:
            raise errors.resource_associated('Line', 'Endpoint',
                                             line_id=line.id,
                                             endpoint=line.endpoint,
                                             endpoint_id=line.endpoint_id)

    def validate_not_associated_to_trunk(self, trunk, endpoint):
        trunk = self.trunk_dao.find_by(endpoint=self.endpoint, endpoint_id=endpoint.id)
        if trunk:
            raise errors.resource_associated('Trunk', 'Endpoint',
                                             trunk_id=trunk.id,
                                             endpoint=trunk.endpoint,
                                             endpoint_id=trunk.endpoint_id)


class ValidateLineDissociation(Validator):

    def __init__(self, user_line_dao, line_extension_dao):
        self.user_line_dao = user_line_dao
        self.line_extension_dao = line_extension_dao

    def validate(self, line, endpoint):
        self.validate_endpoint(line, endpoint)
        self.validate_users(line)
        self.validate_extensions(line)
        ValidateLineHasNoDevice().validate(line)

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

    def validate_device(self, line):
        if line.device_id is not None:
            raise errors.resource_associated('Line', 'Device',
                                             line_id=line.id, device_id=line.device_id)


def build_validator(endpoint):
    return ValidationAssociation(
        association=[
            ValidateLineAssociation(endpoint,
                                    line_dao_module,
                                    trunk_dao_module)
        ],
        dissociation=[
            ValidateLineDissociation(user_line_dao_module,
                                     line_extension_dao_module)
        ]
    )
