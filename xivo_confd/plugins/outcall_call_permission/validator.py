# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_confd.helpers.validator import Validator, ValidationAssociation


class AssociateOutcallCallPermission(Validator):

    def validate(self, outcall, call_permission):
        self.validate_same_tenant(outcall, call_permission)

    def validate_same_tenant(self, outcall, call_permission):
        if outcall.tenant_uuid != call_permission.tenant_uuid:
            raise errors.different_tenants(
                outcall_tenant_uuid=outcall.tenant_uuid,
                call_permission_tenant_uuid=call_permission.tenant_uuid,
            )


def build_validator():
    return ValidationAssociation(
        association=[
            AssociateOutcallCallPermission()
        ]
    )
