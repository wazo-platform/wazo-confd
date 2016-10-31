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
