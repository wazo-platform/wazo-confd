# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


from xivo_confd.helpers.validator import Validator, AssociationValidator

from xivo_dao.helpers import errors
from xivo_dao.resources.line import dao as line_dao_module
from xivo_dao.resources.trunk import dao as trunk_dao_module


class TrunkEndpointAssociationValidator(Validator):

    def __init__(self, endpoint, trunk_dao, line_dao):
        super(TrunkEndpointAssociationValidator, self).__init__()
        self.endpoint = endpoint
        self.trunk_dao = trunk_dao
        self.line_dao = line_dao

    def validate(self, trunk, endpoint):
        self.validate_not_already_associated(trunk, endpoint)
        self.validate_not_associated_to_trunk(trunk, endpoint)
        self.validate_not_associated_to_line(trunk, endpoint)

    def validate_not_already_associated(self, trunk, endpoint):
        if trunk.is_associated():
            raise errors.resource_associated('Trunk', 'Endpoint',
                                             trunk_id=trunk.id,
                                             endpoint=trunk.endpoint,
                                             endpoint_id=trunk.endpoint_id)

    def validate_not_associated_to_trunk(self, trunk, endpoint):
        trunk = self.trunk_dao.find_by(endpoint=self.endpoint, endpoint_id=endpoint.id)
        if trunk:
            raise errors.resource_associated('Trunk', 'Endpoint',
                                             trunk_id=trunk.id,
                                             endpoint=trunk.endpoint,
                                             endpoint_id=trunk.endpoint_id)

    def validate_not_associated_to_line(self, trunk, endpoint):
        line = self.line_dao.find_by(endpoint=self.endpoint, endpoint_id=endpoint.id)
        if line:
            raise errors.resource_associated('Line', 'Endpoint',
                                             trunk_id=line.id,
                                             endpoint=line.endpoint,
                                             endpoint_id=line.endpoint_id)


class TrunkEndpointDissociationValidator(Validator):

    def validate(self, trunk, endpoint):
        self.validate_endpoint(trunk, endpoint)

    def validate_endpoint(self, trunk, endpoint):
        if not trunk.is_associated_with(endpoint):
            raise errors.resource_not_associated('Trunk', 'Endpoint',
                                                 trunk_id=trunk.id,
                                                 endpoint_id=endpoint.id)


def build_validator(endpoint):
    return AssociationValidator(
        association=[
            TrunkEndpointAssociationValidator(endpoint,
                                              trunk_dao_module,
                                              line_dao_module)
        ],
        dissociation=[
            TrunkEndpointDissociationValidator()
        ]
    )
