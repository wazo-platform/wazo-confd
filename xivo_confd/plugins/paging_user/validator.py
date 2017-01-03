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


class PagingUserAssociationValidator(ValidatorAssociation):

    def validate(self, paging, users):
        self.validate_no_duplicate_user(users)

    def validate_no_duplicate_user(self, users):
        if len(users) != len(set(users)):
            raise errors.not_permitted('Cannot associate same user more than once')


def build_validator():
    return ValidationAssociation(
        association=[PagingUserAssociationValidator()],
    )
