# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import AssociationValidator
from xivo_confd.helpers.validator import Validator

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao


class ValidateLineHasNoDevice(Validator):

    def validate(self, line):
        if line.device_id is not None:
            raise errors.resource_associated('Line', 'Device',
                                             line_id=line.id, device_id=line.device_id)


class ValidateLineDeviceAssociation(Validator):

    def validate(self, line, device):
        ValidateLineHasNoDevice().validate(line)


class ValidateLineDeviceDissociation(Validator):

    def validate(self, line, device):
        if line.device_id != device.id:
            raise errors.resource_not_associated('Line', 'Device',
                                                 line_id=line.id, device_id=device.id)


class ValidateLinePosition(Validator):

    def __init__(self, line_dao):
        self.line_dao = line_dao

    def validate(self, line, device):
        existing = self.line_dao.find_by(device_id=device.id, position=line.position)
        if existing:
            msg = "Cannot associate 2 lines with same position (position: {})".format(line.position)
            raise errors.ResourceError(msg)


class ValidateRequiredResources(Validator):

    def __init__(self, user_line_dao, line_extension_dao):
        self.user_line_dao = user_line_dao
        self.line_extension_dao = line_extension_dao

    def validate(self, line, device):
        self.validate_endpoint(line)
        self.validate_extension(line)
        self.validate_user(line)

    def validate_endpoint(self, line):
        if not line.is_associated():
            raise errors.missing_association('Line', 'Endpoint', line_id=line.id)

    def validate_extension(self, line):
        line_extensions = self.line_extension_dao.find_all_by(line_id=line.id)
        if not line_extensions:
            raise errors.missing_association('Line', 'Extension', line_id=line.id)

    def validate_user(self, line):
        user_lines = self.user_line_dao.find_all_by(line_id=line.id)
        if not user_lines:
            raise errors.missing_association('User', 'Line', line_id=line.id)


def build_validator():
    return AssociationValidator(
        association=[
            ValidateLineDeviceAssociation(),
            ValidateLinePosition(line_dao),
            ValidateRequiredResources(user_line_dao, line_extension_dao)
        ],
        dissociation=[
            ValidateLineDeviceDissociation(),
        ]
    )
