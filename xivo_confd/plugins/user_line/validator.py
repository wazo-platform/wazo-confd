# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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


from xivo_confd.database import user_line as user_line_db

from xivo_confd.helpers.validator import Validator, AssociationValidator

from xivo_dao.helpers import errors
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao

from xivo_confd.plugins.line_device.validator import ValidateLineHasNoDevice


class UserLineAssociationValidator(Validator):

    def validate(self, user, line):
        self.validate_line_has_endpoint(line)
        self.validate_user_line_not_already_associated(user, line)
        self.validate_we_are_not_creating_a_group_under_the_same_extension(user, line)

    def validate_line_has_endpoint(self, line):
        if not line.is_associated():
            raise errors.missing_association('Line', 'Endpoint',
                                             line_id=line.id)

    def validate_user_line_not_already_associated(self, user, line):
        user_line = user_line_dao.find_by(user_id=user.id, line_id=line.id)
        if user_line:
            raise errors.resource_associated('User', 'Line',
                                             user_id=user.id,
                                             line_id=line.id)

    def validate_we_are_not_creating_a_group_under_the_same_extension(self, user, line):
        main_line_extension = line_extension_dao.find_by_line_id(line.id)
        if not main_line_extension:
            return

        lines_reachable_from_extension = set(line_extension.line_id for line_extension in line_extension_dao.find_all_by(extension_id=main_line_extension.extension_id))
        users_reachable_from_extension = set(user_line.user_id
                                             for line_id in lines_reachable_from_extension
                                             for user_line in user_line_dao.find_all_by(line_id=line_id, main_user=True))
        users_reachable_from_extension.add(user.id)

        if len(users_reachable_from_extension) == 1:
            return
        elif len(lines_reachable_from_extension) == 1:
            return
        else:
            lines_reachable_from_extension.remove(line.id)
            faulty_line_id = lines_reachable_from_extension.pop()
            raise errors.resource_associated('Line', 'Extension',
                                             line_id=faulty_line_id,
                                             extension_id=main_line_extension.extension_id)


class UserLineDissociationValidator(Validator):

    def validate(self, user, line):
        self.validate_no_secondary_users(user, line)
        ValidateLineHasNoDevice().validate(line)

    def validate_no_secondary_users(self, user, line):
        exists = user_line_db.has_secondary_users(user.id, line.id)
        if exists:
            raise errors.secondary_users(line_id=line.id)


def build_validator():
    return AssociationValidator(
        association=[
            UserLineAssociationValidator()
        ],
        dissociation=[
            UserLineDissociationValidator()
        ]
    )
