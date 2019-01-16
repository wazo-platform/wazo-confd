# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class TrunkRegisterIAXAssociationValidator(ValidatorAssociation):

    def validate(self, trunk, register):
        self.validate_trunk_not_already_associated(trunk, register)
        self.validate_register_not_already_associated(trunk, register)
        self.validate_associate_to_endpoint_iax(trunk, register)

    def validate_trunk_not_already_associated(self, trunk, register):
        if trunk.register_iax:
            raise errors.resource_associated('Trunk', 'IAXRegister',
                                             trunk_id=trunk.id,
                                             register_iax_id=trunk.register_iax.id)

    def validate_register_not_already_associated(self, trunk, register):
        if register.trunk:
            raise errors.resource_associated('Trunk', 'IAXRegister',
                                             trunk_id=register.trunk.id,
                                             register_iax_id=register.id)

    def validate_associate_to_endpoint_iax(self, trunk, register):
        if trunk.endpoint_sip or trunk.endpoint_custom:
            raise errors.resource_associated('Trunk', 'Endpoint',
                                             trunk_id=trunk.id,
                                             protocol=trunk.protocol)


class TrunkRegisterSIPAssociationValidator(ValidatorAssociation):

    def validate(self, trunk, register):
        self.validate_trunk_not_already_associated(trunk, register)
        self.validate_register_not_already_associated(trunk, register)
        self.validate_associate_to_endpoint_sip(trunk, register)

    def validate_trunk_not_already_associated(self, trunk, register):
        if trunk.register_sip:
            raise errors.resource_associated('Trunk', 'SIPRegister',
                                             trunk_id=trunk.id,
                                             register_sip_id=trunk.register_sip.id)

    def validate_register_not_already_associated(self, trunk, register):
        if register.trunk:
            raise errors.resource_associated('Trunk', 'SIPRegister',
                                             trunk_id=register.trunk.id,
                                             register_sip_id=register.id)

    def validate_associate_to_endpoint_sip(self, trunk, register):
        if trunk.endpoint_iax or trunk.endpoint_custom:
            raise errors.resource_associated('Trunk', 'Endpoint',
                                             trunk_id=trunk.id,
                                             protocol=trunk.protocol)


def build_validator_iax():
    return ValidationAssociation(
        association=[
            TrunkRegisterIAXAssociationValidator(),
        ],
    )


def build_validator_sip():
    return ValidationAssociation(
        association=[
            TrunkRegisterSIPAssociationValidator(),
        ],
    )
