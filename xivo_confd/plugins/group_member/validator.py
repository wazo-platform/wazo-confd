# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class GroupMemberUserAssociationValidator(ValidatorAssociation):

    def validate(self, group, members):
        users = [member.user for member in members]
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


class GroupMemberExtensionAssociationValidator(ValidatorAssociation):

    def validate(self, group, members):
        extensions = [{
            'exten': member.extension.exten,
            'context': member.extension.context
        } for member in members]
        self.validate_no_duplicate_extension(extensions)

    def validate_no_duplicate_extension(self, extensions):
        if any(extensions.count(extension) > 1 for extension in extensions):
            raise errors.not_permitted('Cannot associate same extensions more than once')


def build_validator_member_user():
    return ValidationAssociation(
        association=[GroupMemberUserAssociationValidator()],
    )


def build_validator_member_extension():
    return ValidationAssociation(
        association=[GroupMemberExtensionAssociationValidator()],
    )
