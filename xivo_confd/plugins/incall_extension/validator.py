# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class IncallExtensionAssociationValidator(ValidatorAssociation):

    def validate(self, incall, extension):
        self.validate_incall_not_already_associated(incall)
        self.validate_extension_not_already_associated(extension)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_incall_context(extension)

    def validate_incall_not_already_associated(self, incall):
        extension = extension_dao.find_by(type='incall', typeval=str(incall.id))
        if extension:
            raise errors.resource_associated('Incall', 'Extension',
                                             incall_id=extension.typeval,
                                             extension_id=extension.id)

    def validate_extension_not_already_associated(self, extension):
        if extension.type == 'incall':
            raise errors.resource_associated('Incall', 'Extension',
                                             incall_id=extension.typeval,
                                             extension_id=extension.id)

    def validate_extension_not_associated_to_other_resource(self, extension):
        if not (extension.type == 'user' and extension.typeval == '0'):
            raise errors.resource_associated('Extension',
                                             extension.type,
                                             extension_id=extension.id,
                                             associated_id=extension.typeval)

    def validate_extension_is_in_incall_context(self, extension):
        context = context_dao.get_by_name(extension.context)
        if context.type != 'incall':
            raise errors.unhandled_context_type(context.type,
                                                extension.context,
                                                id=extension.id,
                                                context=extension.context)


def build_validator():
    return ValidationAssociation(
        association=[IncallExtensionAssociationValidator()],
    )
