# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.trunk import dao as trunk_dao
from .validator import build_validator
from .notifier import build_notifier

from xivo_dao.helpers import errors


class TrunkEndpointService(object):

    def __init__(self, endpoint, trunk_dao, endpoint_dao, validator, notifier):
        self.endpoint = endpoint
        self.trunk_dao = trunk_dao
        self.endpoint_dao = endpoint_dao
        self.validator = validator
        self.notifier = notifier

    def get_trunk(self, trunk_id):
        return self.trunk_dao.get(trunk_id)

    def get_endpoint(self, endpoint_id):
        return self.endpoint_dao.get(endpoint_id)

    def get_association_from_trunk(self, trunk_id):
        trunk = self.trunk_dao.get(trunk_id)
        if not trunk.is_associated(self.endpoint):
            raise errors.not_found('TrunkEndpoint', trunk_id=trunk_id)

        return {'trunk_id': trunk.id,
                'endpoint': trunk.endpoint,
                'endpoint_id': trunk.endpoint_id}

    def get_association_from_endpoint(self, endpoint_id):
        endpoint = self.endpoint_dao.get(endpoint_id)
        trunk = self.trunk_dao.find_by(protocol=self.endpoint, endpoint_id=endpoint.id)
        if not trunk:
            raise errors.not_found('TrunkEndpoint', endpoint_id=endpoint_id)

        return {'trunk_id': trunk.id,
                'endpoint': trunk.endpoint,
                'endpoint_id': trunk.endpoint_id}

    def associate(self, trunk, endpoint):
        if not trunk.is_associated_with(endpoint):
            self.validator.validate_association(trunk, endpoint)
            trunk.associate_endpoint(endpoint)
            self.trunk_dao.edit(trunk)
        self.notifier.associated(trunk, endpoint)

    def dissociate(self, trunk, endpoint):
        self.validator.validate_dissociation(trunk, endpoint)
        trunk.remove_endpoint()
        self.trunk_dao.edit(trunk)
        self.notifier.dissociated(trunk, endpoint)


def build_service(endpoint, endpoint_dao):
    return TrunkEndpointService(endpoint,
                                trunk_dao,
                                endpoint_dao,
                                build_validator(endpoint),
                                build_notifier(endpoint))
