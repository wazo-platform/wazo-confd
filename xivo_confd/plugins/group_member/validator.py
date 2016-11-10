# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import Validator, AssociationValidator


class GroupMemberUserAssociationValidator(Validator):

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
            raise errors.not_permitted('Cannot associate same user twice')

    def validate_no_users_have_same_line(self, users):
        all_lines = [user.lines[0] for user in users]
        for line in all_lines:
            if all_lines.count(line) > 1:
                raise errors.not_permitted('Cannot associate different users with the same line',
                                           line_id=line.id)


def build_validator():
    return AssociationValidator(
        association=[GroupMemberUserAssociationValidator()],
    )
