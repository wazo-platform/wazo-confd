# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao_module

from wazo_confd.helpers.validator import (
    GetResource,
    Optional,
    ValidationGroup,
    Validator,
)


class ContextTenantValidator(Validator):

    def __init__(self, context_dao_module):
        self.context_dao = context_dao_module

    def validate(self, trunk):
        context = self.context_dao.find_by(name=trunk.context)
        if not context:
            return

        if trunk.tenant_uuid != context.tenant_uuid:
            raise errors.different_tenants(
                trunk_tenant_uuid=trunk.tenant_uuid,
                context_tenant_uuid=context.tenant_uuid
            )


def build_validator():
    return ValidationGroup(
        create=[
            Optional('context', GetResource('context', context_dao_module.get_by_name, 'Context')),
            ContextTenantValidator(context_dao_module),
        ],
        edit=[
            Optional('context', GetResource('context', context_dao_module.get_by_name, 'Context')),
            ContextTenantValidator(context_dao_module),
        ]
    )
