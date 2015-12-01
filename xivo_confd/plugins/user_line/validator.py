# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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


from xivo_dao.helpers.db_manager import Session

from xivo_dao.alchemy.user_line import UserLine

from xivo_confd.helpers.validator import Validator, AssociationValidator

from xivo_dao.helpers import errors


from xivo_confd.resources.line_device import validator as line_device_validator


class UserLineAssociationValidator(Validator):

    def validate(self, user, line):
        self.validate_line_has_endpoint(line)
        self.validate_user_not_already_associated(user)

    def validate_line_has_endpoint(self, line):
        if not line.is_associated():
            raise errors.missing_association('Line', 'Endpoint',
                                             line_id=line.id)

    def validate_user_not_already_associated(self, user):
        line_id = (Session.query(UserLine.user_id)
                   .filter_by(user_id=user.id)
                   .scalar())

        if line_id:
            raise errors.resource_associated('User', 'Line',
                                             user_id=user.id,
                                             line_id=line_id)


class UserLineDissociationValidator(Validator):

    def validate(self, user, line):
        self.validate_no_secondary_users(user, line)
        line_device_validator.validate_no_device(line.id)

    def validate_no_secondary_users(self, user, line):
        exists_query = (Session.query(UserLine)
                        .filter(UserLine.line_id == line.id)
                        .filter(UserLine.user_id != user.id)
                        .filter(UserLine.main_user == False)  # noqa
                        .exists())

        exists = Session.query(exists_query).scalar()
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
