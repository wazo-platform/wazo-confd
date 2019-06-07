# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from wazo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class UserGroupAssociationValidator(ValidatorAssociation):

    def validate(self, user, groups):
        self.validate_user_has_endpoint(user)
        self.validate_no_duplicate_group(groups)

    def validate_user_has_endpoint(self, user):
        if not user.lines:
            raise errors.missing_association('User', 'Line',
                                             user_uuid=user.uuid)

    def validate_no_duplicate_group(self, groups):
        if len(groups) != len(set(groups)):
            raise errors.not_permitted('Cannot associate same group more than once')


def build_validator():
    return ValidationAssociation(
        association=[UserGroupAssociationValidator()],
    )
