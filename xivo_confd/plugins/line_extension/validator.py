# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao_module
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd.helpers.validator import (
    BaseExtensionRangeMixin,
    ValidatorAssociation,
    ValidationAssociation,
)
from xivo_confd.plugins.line_device.validator import ValidateLineHasNoDevice


class LineExtensionAssociationValidator(ValidatorAssociation, BaseExtensionRangeMixin):

    def __init__(self, context_dao):
        self._context_dao = context_dao

    def validate(self, line, extension):
        self.validate_same_tenant(line, extension)
        self.validate_line_has_endpoint(line)
        self.validate_line_has_no_extension(line)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_internal_context(extension)
        self.validate_line_has_no_different_user(line, extension)
        self.validate_exten_is_in_context_user_range(extension)

    def validate_line_has_endpoint(self, line):
        if not line.is_associated():
            raise errors.missing_association('Line', 'Endpoint',
                                             line_id=line.id)

    def validate_line_has_no_extension(self, line):
        line_extension = line_extension_dao.find_by(line_id=line.id)
        if line_extension:
            raise errors.resource_associated('Line', 'Extension',
                                             line_id=line_extension.line_id,
                                             extension_id=line_extension.extension_id)

    def validate_extension_not_associated_to_other_resource(self, extension):
        extension = extension_dao.find_by(id=extension.id)
        if extension.type != 'user':
            raise errors.resource_associated('Extension',
                                             extension.type,
                                             id=extension.id,
                                             associated_id=extension.typeval)

    def validate_extension_is_in_internal_context(self, extension):
        context = self._context_dao.get_by_name(extension.context)
        if context.type != 'internal':
            raise errors.unhandled_context_type(context.type,
                                                extension.context,
                                                id=extension.id,
                                                context=extension.context)

    def validate_line_has_no_different_user(self, line, extension):
        user_line = user_line_dao.find_by(line_id=line.id, main_user=True)
        if not user_line:
            return

        line_extensions = line_extension_dao.find_all_by(extension_id=extension.id)
        for line_extension in line_extensions:
            other_user_line = user_line_dao.find_by(line_id=line_extension.line_id, main_user=True)
            if not other_user_line:
                continue

            if other_user_line.user_id != user_line.user_id:
                raise errors.resource_associated('User', 'Line',
                                                 user_id=other_user_line.user_id,
                                                 line_id=other_user_line.line_id)

    def validate_exten_is_in_context_user_range(self, extension):
        if self._is_pattern(extension.exten):
            return

        context = self._context_dao.get_by_name(extension.context)
        if not self._exten_in_range(extension.exten, context.user_ranges):
            raise errors.outside_context_range(extension.exten, extension.context)

    def validate_same_tenant(self, line, extension):
        if extension.tenant_uuid != line.tenant_uuid:
            raise errors.different_tenants(
                extension_tenant_uuid=extension.tenant_uuid,
                line_tenant_uuid=line.tenant_uuid,
            )


class LineExtensionDissociationValidator(ValidatorAssociation):

    def validate(self, line, extension):
        ValidateLineHasNoDevice().validate(line)


def build_validator():
    return ValidationAssociation(
        association=[LineExtensionAssociationValidator(context_dao_module)],
        dissociation=[LineExtensionDissociationValidator()]
    )
