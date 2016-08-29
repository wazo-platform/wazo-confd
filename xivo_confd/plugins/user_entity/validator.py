# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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


from xivo_confd.helpers.validator import AssociationValidator, Validator
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.helpers import errors


class UserEntityAssociationValidator(Validator):

    def __init__(self, user_line_dao):
        self.user_line_dao = user_line_dao

    def validate(self, user, entity):
        self.validate_user_not_already_associated(user, entity)
        self.validate_user_no_line_associated(user)

    def validate_user_not_already_associated(self, user, entity):
        if user.entity_id == entity.id:
            raise errors.resource_associated('User', 'Entity',
                                             user_id=user.id, entity=entity.id)

    def validate_user_no_line_associated(self, user):
        user_lines = self.user_line_dao.find_all_by(user_id=user.id)
        if user_lines:
            line_ids = ','.join(str(ul.line_id) for ul in user_lines)
            raise errors.resource_associated('User', 'Line',
                                             user_id=user.id,
                                             line_ids=line_ids)


def build_validator():
    return AssociationValidator(
        association=[
            UserEntityAssociationValidator(user_line_dao)
        ]
    )
