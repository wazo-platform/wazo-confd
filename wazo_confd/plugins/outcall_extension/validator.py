# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao

from wazo_confd.helpers.validator import (
    ValidatorAssociation,
    ValidationAssociation,
)


class OutcallExtensionAssociationValidator(ValidatorAssociation):

    def validate(self, outcall, extension):
        self.validate_same_tenant(outcall, extension)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_outcall_context(extension)

    def validate_extension_not_associated_to_other_resource(self, extension):
        if not (extension.type == 'user' and extension.typeval == '0'):
            raise errors.resource_associated('Extension',
                                             extension.type,
                                             extension_id=extension.id,
                                             associated_id=extension.typeval)

    def validate_extension_is_in_outcall_context(self, extension):
        context = context_dao.get_by_name(extension.context)
        if context.type != 'outcall':
            raise errors.unhandled_context_type(context.type,
                                                extension.context,
                                                id=extension.id,
                                                context=extension.context)

    def validate_same_tenant(self, outcall, extension):
        if extension.tenant_uuid != outcall.tenant_uuid:
            raise errors.different_tenants(
                extension_tenant_uuid=extension.tenant_uuid,
                outcall_tenant_uuid=outcall.tenant_uuid
            )


def build_validator():
    return ValidationAssociation(
        association=[OutcallExtensionAssociationValidator()],
    )
