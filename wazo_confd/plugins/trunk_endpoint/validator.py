# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.line import dao as line_dao_module
from xivo_dao.resources.trunk import dao as trunk_dao_module

from wazo_confd.helpers.validator import ValidationAssociation, ValidatorAssociation


class _TrunkEndpointAssociationValidator(ValidatorAssociation):
    def __init__(self, trunk_dao, line_dao):
        super().__init__()
        self.trunk_dao = trunk_dao
        self.line_dao = line_dao

    def validate(self, trunk, endpoint):
        self.validate_same_tenant(trunk, endpoint)
        self.validate_not_already_associated(trunk, endpoint)
        self.validate_not_associated_to_trunk(trunk, endpoint)
        self.validate_not_associated_to_line(trunk, endpoint)
        self.validate_associate_to_register(trunk, endpoint)

    def validate_same_tenant(self, trunk, endpoint):
        if trunk.tenant_uuid != endpoint.tenant_uuid:
            raise errors.different_tenants(
                trunk_tenant_uuid=trunk.tenant_uuid,
                endpoint_tenant_uuid=endpoint.tenant_uuid,
            )

    def validate_not_already_associated(self, trunk, endpoint):
        protocol = None
        if trunk.endpoint_sip_uuid:
            protocol = 'sip'
            protocol_id = trunk.endpoint_sip_uuid
        elif trunk.endpoint_iax_id:
            protocol = 'iax'
            protocol_id = trunk.endpoint_iax_id
        elif trunk.endpoint_custom_id:
            protocol = 'custom'
            protocol_id = trunk.endpoint_custom_id

        if protocol:
            raise errors.resource_associated(
                'Trunk',
                'Endpoint',
                trunk_id=trunk.id,
                endpoint=protocol,
                endpoint_id=protocol_id,
            )

    def validate_not_associated_to_line(self, trunk, endpoint):
        pass

    def validate_associate_to_register(self, trunk, endpoint):
        pass


class TrunkEndpointSIPAssociationValidator(_TrunkEndpointAssociationValidator):
    def validate_not_associated_to_trunk(self, trunk, endpoint):
        other_trunk = self.trunk_dao.find_by(endpoint_sip_uuid=endpoint.uuid)
        if other_trunk:
            raise errors.resource_associated(
                'Trunk',
                'Endpoint',
                trunk_id=other_trunk.id,
                endpoint='sip',
                endpoint_id=endpoint.uuid,
            )

    def validate_not_associated_to_line(self, trunk, endpoint):
        line = self.line_dao.find_by(endpoint_sip_uuid=endpoint.uuid)
        if line:
            raise errors.resource_associated(
                'Line',
                'Endpoint',
                trunk_id=line.id,
                endpoint='sip',
                endpoint_id=endpoint.uuid,
            )

    def validate_associate_to_register(self, trunk, endpoint):
        if trunk.register_iax:
            raise errors.resource_associated(
                'Trunk',
                'IAXRegister',
                trunk_id=trunk.id,
                register_sip_id=trunk.register_iax.id,
            )


class TrunkEndpointIAXAssociationValidator(_TrunkEndpointAssociationValidator):
    def validate_not_associated_to_trunk(self, trunk, endpoint):
        other_trunk = self.trunk_dao.find_by(endpoint_iax_id=endpoint.id)
        if other_trunk:
            raise errors.resource_associated(
                'Trunk',
                'Endpoint',
                trunk_id=other_trunk.id,
                endpoint='iax',
                endpoint_id=endpoint.id,
            )


class TrunkEndpointCustomAssociationValidator(_TrunkEndpointAssociationValidator):
    def validate_not_associated_to_trunk(self, trunk, endpoint):
        other_trunk = self.trunk_dao.find_by(endpoint_custom_id=endpoint.id)
        if other_trunk:
            raise errors.resource_associated(
                'Trunk',
                'Endpoint',
                trunk_id=other_trunk.id,
                endpoint='custom',
                endpoint_id=endpoint.id,
            )

    def validate_not_associated_to_line(self, trunk, endpoint):
        line = self.line_dao.find_by(endpoint_custom_id=endpoint.id)
        if line:
            raise errors.resource_associated(
                'Line',
                'Endpoint',
                trunk_id=line.id,
                endpoint='custom',
                endpoint_id=endpoint.id,
            )

    def validate_associate_to_register(self, trunk, endpoint):
        if trunk.register_iax:
            raise errors.resource_associated(
                'Trunk',
                'IAXRegister',
                trunk_id=trunk.id,
                register_iax_id=trunk.register_iax.id,
            )


def build_validator_sip():
    return ValidationAssociation(
        association=[
            TrunkEndpointSIPAssociationValidator(trunk_dao_module, line_dao_module)
        ]
    )


def build_validator_iax():
    return ValidationAssociation(
        association=[
            TrunkEndpointIAXAssociationValidator(trunk_dao_module, line_dao_module)
        ]
    )


def build_validator_custom():
    return ValidationAssociation(
        association=[
            TrunkEndpointCustomAssociationValidator(trunk_dao_module, line_dao_module)
        ]
    )
