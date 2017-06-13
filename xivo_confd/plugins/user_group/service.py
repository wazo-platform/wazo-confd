# -*- coding: UTF-8 -*-

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

from .notifier import build_notifier
from .validator import build_validator

from xivo_dao.resources.user import dao as user_dao


class UserGroupService(object):

    def __init__(self, user_dao, notifier, validator):
        self.user_dao = user_dao
        self.validator = validator
        self.notifier = notifier

    def associate_all_groups(self, user, groups):
        self.validator.validate_association(user, groups)
        self.user_dao.associate_all_groups(user, groups)
        self.notifier.associated(user, groups)


def build_service():
    return UserGroupService(user_dao,
                            build_notifier(),
                            build_validator())
