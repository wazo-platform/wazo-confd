# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.line_extension import dao as line_extension_dao
from xivo_dao.resources.user_line import dao as user_line_dao

from wazo_confd.helpers.validator import ValidationAssociation, ValidatorAssociation
from wazo_confd.plugins.line_device.validator import ValidateLineHasNoDevice


class UserLineAssociationValidator(ValidatorAssociation):
    def validate(self, user, line):
        self.validate_same_tenant(user, line)
        self.validate_line_has_endpoint(line)
        self.validate_we_are_not_creating_a_group_under_the_same_extension(user, line)

    def validate_line_has_endpoint(self, line):
        if not line.is_associated():
            raise errors.missing_association('Line', 'Endpoint', line_id=line.id)

    def validate_we_are_not_creating_a_group_under_the_same_extension(self, user, line):
        main_line_extension = line_extension_dao.find_by_line_id(line.id)
        if not main_line_extension:
            return

        lines_reachable_from_extension = set(
            line_extension.line_id
            for line_extension in line_extension_dao.find_all_by(
                extension_id=main_line_extension.extension_id
            )
        )

        users_reachable_from_extension = set(
            user_line.user_id
            for line_id in lines_reachable_from_extension
            for user_line in user_line_dao.find_all_by(line_id=line_id, main_user=True)
        )
        users_reachable_from_extension.add(user.id)

        if len(users_reachable_from_extension) == 1:
            return
        elif len(lines_reachable_from_extension) == 1:
            return
        else:
            lines_reachable_from_extension.remove(line.id)
            faulty_line_id = lines_reachable_from_extension.pop()
            raise errors.resource_associated(
                'Line',
                'Extension',
                line_id=faulty_line_id,
                extension_id=main_line_extension.extension_id,
            )

    def validate_same_tenant(self, user, line):
        if user.tenant_uuid != line.tenant_uuid:
            raise errors.different_tenants(
                user_tenant_uuid=user.tenant_uuid, line_tenant_uuid=line.tenant_uuid
            )


class UserLineDissociationValidator(ValidatorAssociation):
    def validate(self, user, line):
        self.validate_no_secondary_users(user, line)
        ValidateLineHasNoDevice().validate(line)

    def validate_no_secondary_users(self, user, line):
        user_line = user_line_dao.find_by(line_id=line.id, main_user=False)
        if user_line and user_line.user_id != user.id:
            raise errors.secondary_users(line_id=line.id)


def build_validator():
    return ValidationAssociation(
        association=[UserLineAssociationValidator()],
        dissociation=[UserLineDissociationValidator()],
    )
