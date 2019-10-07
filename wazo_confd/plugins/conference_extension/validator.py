# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.context import dao as context_dao_module

from wazo_confd.helpers.validator import (
    BaseExtensionRangeMixin,
    ValidatorAssociation,
    ValidationAssociation,
)


class ConferenceExtensionAssociationValidator(
    ValidatorAssociation, BaseExtensionRangeMixin
):
    def __init__(self, context_dao):
        self._context_dao = context_dao

    def validate(self, conference, extension):
        self.validate_same_tenant(conference, extension)
        self.validate_conference_not_already_associated(conference)
        self.validate_extension_not_already_associated(extension)
        self.validate_extension_not_associated_to_other_resource(extension)
        self.validate_extension_is_in_internal_context(extension)
        self.validate_exten_is_in_context_conference_range(extension)

    def validate_conference_not_already_associated(self, conference):
        if conference.extensions:
            raise errors.resource_associated(
                'Conference',
                'Extension',
                conference_id=conference.id,
                extension_id=conference.extensions[0].id,
            )

    def validate_extension_not_already_associated(self, extension):
        if extension.conference:
            raise errors.resource_associated(
                'Conference',
                'Extension',
                conference_id=extension.conference.id,
                extension_id=extension.id,
            )

    def validate_extension_not_associated_to_other_resource(self, extension):
        if not (extension.type == 'user' and extension.typeval == '0'):
            raise errors.resource_associated(
                'Extension',
                extension.type,
                extension_id=extension.id,
                associated_id=extension.typeval,
            )

    def validate_extension_is_in_internal_context(self, extension):
        context = self._context_dao.get_by_name(extension.context)
        if context.type != 'internal':
            raise errors.unhandled_context_type(
                context.type,
                extension.context,
                id=extension.id,
                context=extension.context,
            )

    def validate_exten_is_in_context_conference_range(self, extension):
        if self._is_pattern(extension.exten):
            return

        context = self._context_dao.get_by_name(extension.context)
        if not self._exten_in_range(extension.exten, context.conference_room_ranges):
            raise errors.outside_context_range(extension.exten, extension.context)

    def validate_same_tenant(self, conference, extension):
        if extension.tenant_uuid != conference.tenant_uuid:
            raise errors.different_tenants(
                extension_tenant_uuid=extension.tenant_uuid,
                conference_tenant_uuid=conference.tenant_uuid,
            )


def build_validator():
    return ValidationAssociation(
        association=[ConferenceExtensionAssociationValidator(context_dao_module)]
    )
