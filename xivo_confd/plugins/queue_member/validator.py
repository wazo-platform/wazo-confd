# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class QueueMemberUserAssociationValidator(ValidatorAssociation):

    def validate(self, queue, member):
        self.validate_user_has_endpoint(member.user)
        self.validate_no_users_have_same_line(queue, member.user)

    def validate_user_has_endpoint(self, user):
        if not user.lines:
            raise errors.missing_association('User', 'Line',
                                             user_uuid=user.uuid)

    def validate_no_users_have_same_line(self, queue, user):
        all_lines = [member.user.lines[0] for member in queue.user_queue_members]
        if user.lines[0] in all_lines:
            raise errors.not_permitted('Cannot associate different users with the same line',
                                       line_id=user.lines[0].id)


def build_validator_member_user():
    return ValidationAssociation(
        association=[QueueMemberUserAssociationValidator()],
    )
