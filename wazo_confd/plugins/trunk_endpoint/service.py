# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.trunk import dao as trunk_dao_module

from .notifier import build_notifier
from .validator import build_validator


class TrunkEndpointService:
    def __init__(self, endpoint, trunk_dao, validator, notifier):
        self.endpoint = endpoint
        self.trunk_dao = trunk_dao
        self.validator = validator
        self.notifier = notifier

    def associate(self, trunk, endpoint):
        if trunk.is_associated_with(endpoint):
            return

        self.validator.validate_association(trunk, endpoint)
        trunk.associate_endpoint(endpoint)
        self.trunk_dao.edit(trunk)
        self.notifier.associated(trunk, endpoint)

    def dissociate(self, trunk, endpoint):
        if not trunk.is_associated_with(endpoint):
            return

        self.validator.validate_dissociation(trunk, endpoint)
        trunk.remove_endpoint()
        self.trunk_dao.edit(trunk)
        self.notifier.dissociated(trunk, endpoint)


def build_service(endpoint):
    return TrunkEndpointService(
        endpoint, trunk_dao_module, build_validator(endpoint), build_notifier(endpoint),
    )
