# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from wazo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class TrunkRegisterIAXAssociationValidator(ValidatorAssociation):
    def validate(self, trunk, register):
        self.validate_trunk_not_already_associated(trunk, register)
        self.validate_register_not_already_associated(trunk, register)
        self.validate_associate_to_endpoint_iax(trunk, register)

    def validate_trunk_not_already_associated(self, trunk, register):
        if trunk.register_iax:
            raise errors.resource_associated(
                'Trunk',
                'IAXRegister',
                trunk_id=trunk.id,
                register_iax_id=trunk.register_iax.id,
            )

    def validate_register_not_already_associated(self, trunk, register):
        if register.trunk:
            raise errors.resource_associated(
                'Trunk',
                'IAXRegister',
                trunk_id=register.trunk.id,
                register_iax_id=register.id,
            )

    def validate_associate_to_endpoint_iax(self, trunk, register):
        if trunk.endpoint_sip or trunk.endpoint_custom:
            raise errors.resource_associated(
                'Trunk', 'Endpoint', trunk_id=trunk.id, protocol=trunk.protocol
            )


def build_validator_iax():
    return ValidationAssociation(association=[TrunkRegisterIAXAssociationValidator()])
