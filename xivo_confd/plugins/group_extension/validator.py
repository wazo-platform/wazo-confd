# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao_module

from xivo_confd.helpers.validator import (
    BaseExtensionRangeMixin,
    ValidatorAssociation,
    ValidationAssociation,
)


class GroupExtensionAssociationValidator(ValidatorAssociation, BaseExtensionRangeMixin):

    def __init__(self, context_dao):
        self._context_dao = context_dao

    def validate(self, group, extension):
        self.validate_group_not_already_associated(group)
        self.validate_extension_not_already_associated(extension)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_internal_context(extension)
        self.validate_exten_is_in_context_group_range(extension)
        self.validate_same_tenant(group, extension)

    def validate_group_not_already_associated(self, group):
        if group.extensions:
            raise errors.resource_associated('Group', 'Extension',
                                             group_id=group.id,
                                             extension_id=group.extensions[0].id)

    def validate_extension_not_already_associated(self, extension):
        if extension.group:
            raise errors.resource_associated('Group', 'Extension',
                                             group_id=extension.group.id,
                                             extension_id=extension.id)

    def validate_extension_not_associated_to_other_resource(self, extension):
        if not (extension.type == 'user' and extension.typeval == '0'):
            raise errors.resource_associated('Extension',
                                             extension.type,
                                             extension_id=extension.id,
                                             associated_id=extension.typeval)

    def validate_extension_is_in_internal_context(self, extension):
        context = self._context_dao.get_by_name(extension.context)
        if context.type != 'internal':
            raise errors.unhandled_context_type(context.type,
                                                extension.context,
                                                id=extension.id,
                                                context=extension.context)

    def validate_exten_is_in_context_group_range(self, extension):
        if self._is_pattern(extension.exten):
            return

        context = self._context_dao.get_by_name(extension.context)
        if not self._exten_in_range(extension.exten, context.group_ranges):
            raise errors.outside_context_range(extension.exten, extension.context)

    def validate_same_tenant(self, group, extension):
        if extension.tenant_uuid != group.tenant_uuid:
            raise errors.different_tenants(extension.tenant_uuid, group.tenant_uuid)


def build_validator():
    return ValidationAssociation(
        association=[GroupExtensionAssociationValidator(context_dao_module)],
    )
