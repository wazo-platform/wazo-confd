# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.trunk import dao as trunk_dao_module

from .notifier import build_notifier_custom, build_notifier_iax, build_notifier_sip
from .validator import build_validator_custom, build_validator_iax, build_validator_sip


class TrunkEndpointService:
    def __init__(self, trunk_dao, validator, notifier):
        self.trunk_dao = trunk_dao
        self.validator = validator
        self.notifier = notifier


class TrunkEndpointSIPService(TrunkEndpointService):
    def associate(self, trunk, endpoint):
        if trunk.endpoint_sip_uuid == endpoint.uuid:
            return

        self.validator.validate_association(trunk, endpoint)
        self.trunk_dao.associate_endpoint_sip(trunk, endpoint)
        self.notifier.associated(trunk, endpoint)

    def dissociate(self, trunk, endpoint):
        if trunk.endpoint_sip_uuid != endpoint.uuid:
            return

        self.validator.validate_dissociation(trunk, endpoint)
        self.trunk_dao.dissociate_endpoint_sip(trunk, endpoint)
        self.notifier.dissociated(trunk, endpoint)


class TrunkEndpointIAXService(TrunkEndpointService):
    def associate(self, trunk, endpoint):
        if trunk.endpoint_iax_id == endpoint.id:
            return

        self.validator.validate_association(trunk, endpoint)
        self.trunk_dao.associate_endpoint_iax(trunk, endpoint)
        self.notifier.associated(trunk, endpoint)

    def dissociate(self, trunk, endpoint):
        if trunk.endpoint_iax_id != endpoint.id:
            return

        self.validator.validate_dissociation(trunk, endpoint)
        self.trunk_dao.dissociate_endpoint_iax(trunk, endpoint)
        self.notifier.dissociated(trunk, endpoint)


class TrunkEndpointCustomService(TrunkEndpointService):
    def associate(self, trunk, endpoint):
        if trunk.endpoint_custom_id == endpoint.id:
            return

        self.validator.validate_association(trunk, endpoint)
        self.trunk_dao.associate_endpoint_custom(trunk, endpoint)
        self.notifier.associated(trunk, endpoint)

    def dissociate(self, trunk, endpoint):
        if trunk.endpoint_custom_id != endpoint.id:
            return

        self.validator.validate_dissociation(trunk, endpoint)
        self.trunk_dao.dissociate_endpoint_custom(trunk, endpoint)
        self.notifier.dissociated(trunk, endpoint)


def build_service_sip():
    return TrunkEndpointSIPService(
        trunk_dao_module,
        build_validator_sip(),
        build_notifier_sip(),
    )


def build_service_iax():
    return TrunkEndpointIAXService(
        trunk_dao_module,
        build_validator_iax(),
        build_notifier_iax(),
    )


def build_service_custom():
    return TrunkEndpointCustomService(
        trunk_dao_module,
        build_validator_custom(),
        build_notifier_custom(),
    )
