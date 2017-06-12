# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


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
