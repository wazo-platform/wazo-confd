# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class GroupMemberUserAssociationValidator(ValidatorAssociation):

    def validate(self, group, users):
        for user in users:
            self.validate_user_has_endpoint(user)

        self.validate_no_duplicate_user(users)
        self.validate_no_users_have_same_line(users)

    def validate_user_has_endpoint(self, user):
        if not user.lines:
            raise errors.missing_association('User', 'Line',
                                             user_uuid=user.uuid)

    def validate_no_duplicate_user(self, users):
        if len(users) != len(set(users)):
            raise errors.not_permitted('Cannot associate same user more than once')

    def validate_no_users_have_same_line(self, users):
        all_lines = [user.lines[0] for user in users]
        for line in all_lines:
            if all_lines.count(line) > 1:
                raise errors.not_permitted('Cannot associate different users with the same line',
                                           line_id=line.id)


def build_validator():
    return ValidationAssociation(
        association=[GroupMemberUserAssociationValidator()],
    )
