# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from wazo_confd.helpers.validator import ValidationAssociation, ValidatorAssociation


class UserGroupAssociationValidator(ValidatorAssociation):
    def validate(self, user, groups):
        # if there is no group to associate to the user, lines are not required
        if groups:
            self.validate_user_has_endpoint(user)
        self.validate_no_duplicate_group(groups)
        self.validate_same_tenant(user, groups)

    def validate_user_has_endpoint(self, user):
        if not user.lines:
            raise errors.missing_association('User', 'Line', user_uuid=user.uuid)

    def validate_no_duplicate_group(self, groups):
        if len(groups) != len(set(groups)):
            raise errors.not_permitted('Cannot associate same group more than once')

    def validate_same_tenant(self, user, groups):
        for group in groups:
            if group.tenant_uuid != user.tenant_uuid:
                raise errors.different_tenants(
                    user_tenant_uuid=user.tenant_uuid,
                    group_tenant_uuid=group.tenant_uuid,
                )


def build_validator():
    return ValidationAssociation(association=[UserGroupAssociationValidator()])
