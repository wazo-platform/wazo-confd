# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.line import dao as line_dao_module
from xivo_dao.resources.trunk import dao as trunk_dao_module

from wazo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class TrunkEndpointAssociationValidator(ValidatorAssociation):
    def __init__(self, endpoint, trunk_dao, line_dao):
        super().__init__()
        self.endpoint = endpoint
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
        if trunk.is_associated():
            protocol = 'unknown'
            protocol_id = 0
            if trunk.endpoint_sip_uuid:
                protocol = 'sip'
                protocol_id = trunk.endpoint_sip_uuid
            elif trunk.endpoint_iax_id:
                protocol = 'iax'
                protocol_id = trunk.endpoint_iax_id
            elif trunk.endpoint_custom_id:
                protocol = 'custom'
                protocol_id = trunk.endpoint_custom_id
            raise errors.resource_associated(
                'Trunk',
                'Endpoint',
                trunk_id=trunk.id,
                endpoint=protocol,
                endpoint_id=protocol_id,
            )

    def validate_not_associated_to_trunk(self, trunk, endpoint):
        if self.endpoint == 'sip':
            id_ = endpoint.uuid
            trunk = self.trunk_dao.find_by(endpoint_sip_uuid=id_)
        elif self.endpoint == 'iax':
            id_ = endpoint.id
            trunk = self.trunk_dao.find_by(endpoint_iax_id=id_)
        elif self.endpoint == 'custom':
            id_ = endpoint.id
            trunk = self.trunk_dao.find_by(endpoint_custom_id=id_)
        else:
            trunk = None
        if trunk:
            raise errors.resource_associated(
                'Trunk',
                'Endpoint',
                trunk_id=trunk.id,
                endpoint=self.endpoint,
                endpoint_id=id_,
            )

    def validate_not_associated_to_line(self, trunk, endpoint):
        if self.endpoint == 'sip':
            id_ = endpoint.uuid
            line = self.line_dao.find_by(endpoint_sip_uuid=id_)
        elif self.endpoint == 'sccp':
            id_ = endpoint.id
            line = self.line_dao.find_by(endpoint_sccp_id=id_)
        elif self.endpoint == 'custom':
            id_ = endpoint.id
            line = self.line_dao.find_by(endpoint_custom_id=id_)
        else:
            line = None

        if line:
            raise errors.resource_associated(
                'Line',
                'Endpoint',
                trunk_id=line.id,
                endpoint=self.endpoint,
                endpoint_id=id_,
            )

    def validate_associate_to_register(self, trunk, endpoint):
        if self.endpoint == 'sip' and trunk.register_iax:
            raise errors.resource_associated(
                'Trunk',
                'IAXRegister',
                trunk_id=trunk.id,
                register_iax_id=trunk.register_iax.id,
            )
        if self.endpoint == 'custom' and trunk.register_iax:
            raise errors.resource_associated(
                'Trunk',
                'IAXRegister',
                trunk_id=trunk.id,
                register_iax_id=trunk.register_iax.id,
            )


def build_validator(endpoint):
    return ValidationAssociation(
        association=[
            TrunkEndpointAssociationValidator(
                endpoint, trunk_dao_module, line_dao_module
            )
        ]
    )
