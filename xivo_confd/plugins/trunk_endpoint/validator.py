# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation

from xivo_dao.helpers import errors
from xivo_dao.resources.line import dao as line_dao_module
from xivo_dao.resources.trunk import dao as trunk_dao_module


class TrunkEndpointAssociationValidator(ValidatorAssociation):

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


def build_validator(endpoint):
    return ValidationAssociation(
        association=[
            TrunkEndpointAssociationValidator(endpoint,
                                              trunk_dao_module,
                                              line_dao_module)
        ],
    )
