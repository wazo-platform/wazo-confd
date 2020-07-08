# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.line import dao as line_dao_module
from xivo_dao.resources.line_extension import dao as line_extension_dao_module
from xivo_dao.resources.trunk import dao as trunk_dao_module
from xivo_dao.resources.user_line import dao as user_line_dao_module

from wazo_confd.helpers.validator import ValidationAssociation
from wazo_confd.helpers.validator import ValidatorAssociation
from wazo_confd.plugins.line_device.validator import ValidateLineHasNoDevice


class _ValidateLineAssociation(ValidatorAssociation):
    def __init__(self, line_dao, trunk_dao):
        super().__init__()
        self.line_dao = line_dao
        self.trunk_dao = trunk_dao

    def validate(self, line, endpoint):
        self.validate_same_tenant(line, endpoint)
        self.validate_not_already_associated(line, endpoint)
        self.validate_not_associated_to_line(line, endpoint)
        self.validate_not_associated_to_trunk(line, endpoint)

    def validate_same_tenant(self, line, endpoint):
        if line.tenant_uuid != endpoint.tenant_uuid:
            raise errors.different_tenants(
                line_tenant_uuid=line.tenant_uuid,
                endpoint_tenant_uuid=endpoint.tenant_uuid,
            )

    def validate_not_already_associated(self, line, endpoint):
        protocol = None
        if line.endpoint_sip_uuid:
            protocol = 'sip'
            protocol_id = line.endpoint_sip_uuid
        elif line.endpoint_sccp_id:
            protocol = 'sccp'
            protocol_id = line.endpoint_sccp_id
        elif line.endpoint_custom_id:
            protocol = 'custom'
            protocol_id = line.endpoint_custom_id

        if protocol:
            raise errors.resource_associated(
                'Line',
                'Endpoint',
                line_id=line.id,
                endpoint=protocol,
                endpoint_id=protocol_id,
            )

    def validate_not_associated_to_line(self, line, endpoint):
        pass

    def validate_not_associated_to_trunk(self, trunk, endpoint):
        pass


class ValidateLineSIPAssociation(_ValidateLineAssociation):
    def validate_not_associated_to_line(self, line, endpoint):
        line = self.line_dao.find_by(endpoint_sip_uuid=endpoint.uuid)
        if line:
            raise errors.resource_associated(
                'Line',
                'Endpoint',
                line_id=line.id,
                endpoint='sip',
                endpoint_uuid=endpoint.uuid,
            )

    def validate_not_associated_to_trunk(self, trunk, endpoint):
        trunk = self.trunk_dao.find_by(endpoint_sip_uuid=endpoint.uuid)
        if trunk:
            raise errors.resource_associated(
                'Trunk',
                'Endpoint',
                trunk_id=trunk.id,
                endpoint='sip',
                endpoint_uuid=endpoint.uuid,
            )


class ValidateLineSCCPAssociation(_ValidateLineAssociation):
    def validate_not_associated_to_line(self, line, endpoint):
        line = self.line_dao.find_by(endpoint_sccp_id=endpoint.id)
        if line:
            raise errors.resource_associated(
                'Line',
                'Endpoint',
                line_id=line.id,
                endpoint='sccp',
                endpoint_id=endpoint.id,
            )


class ValidateLineCustomAssociation(_ValidateLineAssociation):
    def validate_not_associated_to_line(self, line, endpoint):
        line = self.line_dao.find_by(endpoint_custom_id=endpoint.id)
        if line:
            raise errors.resource_associated(
                'Line',
                'Endpoint',
                line_id=line.id,
                endpoint='custom',
                endpoint_id=endpoint.id,
            )

    def validate_not_associated_to_trunk(self, trunk, endpoint):
        trunk = self.trunk_dao.find_by(endpoint_custom_id=endpoint.id)
        if trunk:
            raise errors.resource_associated(
                'Trunk',
                'Endpoint',
                trunk_id=trunk.id,
                endpoint='custom',
                endpoint_id=endpoint.id,
            )


class ValidateLineDissociation(ValidatorAssociation):
    def __init__(self, user_line_dao, line_extension_dao):
        self.user_line_dao = user_line_dao
        self.line_extension_dao = line_extension_dao

    def validate(self, line, endpoint):
        self.validate_users(line)
        self.validate_extensions(line)
        ValidateLineHasNoDevice().validate(line)

    def validate_users(self, line):
        user_lines = self.user_line_dao.find_all_by_line_id(line.id)
        if user_lines:
            user_ids = ','.join(str(ul.user_id) for ul in user_lines)
            raise errors.resource_associated(
                'Line', 'User', line_id=line.id, user_ids=user_ids
            )

    def validate_extensions(self, line):
        line_extensions = self.line_extension_dao.find_all_by_line_id(line.id)
        if line_extensions:
            extension_ids = ','.join(str(le.extension_id) for le in line_extensions)
            raise errors.resource_associated(
                'Line', 'Extension', line_id=line.id, extension_ids=extension_ids
            )

    def validate_device(self, line):
        if line.device_id is not None:
            raise errors.resource_associated(
                'Line', 'Device', line_id=line.id, device_id=line.device_id
            )


def build_validator_sip():
    return ValidationAssociation(
        association=[
            ValidateLineSIPAssociation(line_dao_module, trunk_dao_module)
        ],
        dissociation=[
            ValidateLineDissociation(user_line_dao_module, line_extension_dao_module)
        ],
    )


def build_validator_sccp():
    return ValidationAssociation(
        association=[
            ValidateLineSCCPAssociation(line_dao_module, trunk_dao_module)
        ],
        dissociation=[
            ValidateLineDissociation(user_line_dao_module, line_extension_dao_module)
        ],
    )


def build_validator_custom():
    return ValidationAssociation(
        association=[
            ValidateLineCustomAssociation(line_dao_module, trunk_dao_module)
        ],
        dissociation=[
            ValidateLineDissociation(user_line_dao_module, line_extension_dao_module)
        ],
    )
