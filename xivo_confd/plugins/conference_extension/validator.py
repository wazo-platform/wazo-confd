# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class ConferenceExtensionAssociationValidator(ValidatorAssociation):

    def validate(self, conference, extension):
        if extension in conference.extensions:
            return
        self.validate_conference_not_already_associated(conference)
        self.validate_extension_not_already_associated(extension)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_internal_context(extension)

    def validate_conference_not_already_associated(self, conference):
        if conference.extensions:
            raise errors.resource_associated('Conference', 'Extension',
                                             conference_id=conference.id,
                                             extension_id=conference.extensions[0].id)

    def validate_extension_not_already_associated(self, extension):
        if extension.conference:
            raise errors.resource_associated('Conference', 'Extension',
                                             conference_id=extension.conference.id,
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


def build_validator():
    return ValidationAssociation(
        association=[ConferenceExtensionAssociationValidator()],
    )
