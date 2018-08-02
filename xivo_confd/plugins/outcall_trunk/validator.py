# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class GroupTrunkAssociationValidator(ValidatorAssociation):

    def validate(self, outcall, trunks):
        for trunk in trunks:
            self.validate_same_tenant(outcall, trunk)
        self.validate_no_duplicate_trunk(trunks)

    def validate_same_tenant(self, outcall, trunk):
        if outcall.tenant_uuid != trunk.tenant_uuid:
            raise errors.different_tenants(
                outcall_tenant_uuid=outcall.tenant_uuid,
                trunk_tenant_uuid=trunk.tenant_uuid
            )

    def validate_no_duplicate_trunk(self, trunks):
        if len(trunks) != len(set(trunks)):
            raise errors.not_permitted('Cannot associate same trunk more than once')


def build_validator():
    return ValidationAssociation(
        association=[GroupTrunkAssociationValidator()],
    )
