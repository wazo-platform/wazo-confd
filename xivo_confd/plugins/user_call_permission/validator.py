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


from xivo_confd.helpers.validator import Validator, ValidationAssociation

from xivo_dao.helpers import errors
from xivo_dao.resources.user_call_permission import dao as user_call_permission_dao


class UserCallPermissionAssociationValidator(Validator):

    def validate(self, user, call_permission):
        self.validate_user_not_already_associated(user, call_permission)

    def validate_user_not_already_associated(self, user, call_permission):
        user_call_permission = user_call_permission_dao.find_by(user_id=user.id,
                                                                call_permission_id=call_permission.id)
        if user_call_permission:
            raise errors.resource_associated('User', 'CallPermission',
                                             user_id=user.id, call_permission_id=call_permission.id)


def build_validator():
    return ValidationAssociation(
        association=[
            UserCallPermissionAssociationValidator()
        ]
    )
