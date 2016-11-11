# -*- coding: UTF-8 -*-

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

from .notifier import build_notifier
from .validator import build_validator

from xivo_dao.resources.group import dao as group_dao


class GroupMemberUserService(object):

    def __init__(self, group_dao, notifier, validator):
        self.group_dao = group_dao
        self.validator = validator
        self.notifier = notifier

    def associate_all_users(self, group, users):
        self.validator.validate_association(group, users)
        self.group_dao.associate_all_member_users(group, users)
        self.notifier.associated(group, users)


def build_service():
    return GroupMemberUserService(group_dao,
                                  build_notifier(),
                                  build_validator())
