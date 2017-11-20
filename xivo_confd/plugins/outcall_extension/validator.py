# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class OutcallExtensionAssociationValidator(ValidatorAssociation):

    def validate(self, outcall, extension):
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


class OutcallExtensionDissociationValidator(ValidatorAssociation):

    def validate(self, outcall, extension):
        self.validate_outcall_extension_exists(outcall, extension)

    def validate_outcall_extension_exists(self, outcall, extension):
        if extension not in outcall.extensions:
            raise errors.not_found('OutcallExtension',
                                   outcall_id=outcall.id,
                                   extension_id=extension.id)


def build_validator():
    return ValidationAssociation(
        association=[OutcallExtensionAssociationValidator()],
        dissociation=[OutcallExtensionDissociationValidator()]
    )
