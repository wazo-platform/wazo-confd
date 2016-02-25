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


def build_validator():
    return AssociationValidator(
        association=[
            ValidateLineDeviceAssociation(),
        ],
        dissociation=[
            ValidateLineDeviceDissociation(),
        ]
    )
