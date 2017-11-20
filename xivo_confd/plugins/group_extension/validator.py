# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class GroupExtensionAssociationValidator(ValidatorAssociation):

    def validate(self, group, extension):
        self.validate_group_not_already_associated(group)
        self.validate_extension_not_already_associated(extension)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_internal_context(extension)

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
        context = context_dao.get_by_name(extension.context)
        if context.type != 'internal':
            raise errors.unhandled_context_type(context.type,
                                                extension.context,
                                                id=extension.id,
                                                context=extension.context)


class GroupExtensionDissociationValidator(ValidatorAssociation):

    def validate(self, group, extension):
        self.validate_group_extension_exists(group, extension)

    def validate_group_extension_exists(self, group, extension):
        if extension.group != group:
            raise errors.not_found('GroupExtension',
                                   group_id=group.id,
                                   extension_id=extension.id)


def build_validator():
    return ValidationAssociation(
        association=[GroupExtensionAssociationValidator()],
        dissociation=[GroupExtensionDissociationValidator()]
    )
