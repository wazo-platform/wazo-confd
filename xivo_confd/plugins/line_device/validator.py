# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.line import dao as line_dao_module
from xivo_dao.resources.line_extension import dao as line_extension_dao_module
from xivo_dao.resources.user_line import dao as user_line_dao_module

from xivo_confd.helpers.validator import (
    ValidationAssociation,
    Validator,
    ValidatorAssociation,
)


class ValidateLineHasNoDevice(Validator):

    def validate(self, line):
        if line.device_id is not None:
            raise errors.resource_associated('Line', 'Device',
                                             line_id=line.id, device_id=line.device_id)


class ValidateLineDeviceAssociation(ValidatorAssociation):

    def validate(self, line, device):
        self.validate_same_tenant(line, device)
        ValidateLineHasNoDevice().validate(line)

    def validate_same_tenant(self, line, device):
        if not device.is_new and line.tenant_uuid != device.tenant_uuid:
            raise errors.different_tenants(
                line_tenant_uuid=line.tenant_uuid,
                device_tenant_uuid=device.tenant_uuid,
            )


class ValidateLinePosition(ValidatorAssociation):

    def __init__(self, line_dao):
        self.line_dao = line_dao

    def validate(self, line, device):
        existing = self.line_dao.find_by(device_id=device.id, position=line.position)
        if existing:
            msg = "Cannot associate 2 lines with same position (position: {})".format(line.position)
            raise errors.ResourceError(msg)


class ValidateRequiredResources(ValidatorAssociation):

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


class ValidateMultipleLines(ValidatorAssociation):

    def __init__(self, line_dao):
        self.line_dao = line_dao

    def validate(self, line, device):
        lines = self.line_dao.find_all_by(device_id=device.id)
        if lines:
            existing = lines[0]
            # Multiple lines associated to a SCCP device is not supported
            if existing.endpoint == "sccp" or line.endpoint == "sccp":
                raise errors.resource_associated('Line', 'Device',
                                                 line_id=line.id, device_id=device.id,
                                                 endpoint=line.endpoint, endpoint_id=line.endpoint_id)


def build_validator():
    return ValidationAssociation(
        association=[
            ValidateLineDeviceAssociation(),
            ValidateLinePosition(line_dao_module),
            ValidateRequiredResources(user_line_dao_module, line_extension_dao_module),
            ValidateMultipleLines(line_dao_module),
        ]
    )
