# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_confd.plugins.user_line import validator, notifier


class UserLineService(object):

    def __init__(self, dao, user_dao, line_dao, validator, notifier):
        self.dao = dao
        self.user_dao = user_dao
        self.line_dao = line_dao
        self.validator = validator
        self.notifier = notifier

    def validate_parent(self, user_id):
        self.user_dao.get(user_id)

    def validate_resource(self, line_id):
        self.line_dao.get(line_id)

    def list(self, user_id):
        return self.dao.find_all_by_user_id(user_id)

    def get(self, user_id, line_id):
        return self.dao.get_by_user_id_and_line_id(user_id, line_id)

    def associate(self, user_line):
        self.validator.validate_association(user_line)
        self._adjust_optional_parameters(user_line)
        user_line = self.dao.associate(user_line)
        self.notifier.associated(user_line)
        return user_line

    def dissociate(self, user_line):
        self.validator.validate_dissociation(user_line)
        self.dao.dissociate(user_line)
        self.notifier.dissociated(user_line)

    def _adjust_optional_parameters(self, user_line):
        user_line_main_user = self.dao.find_main_user_line(user_line.line_id)
        if user_line_main_user is not None:
            user_line.main_user = (user_line.user_id == user_line_main_user.user_id)


def build_service():
    return UserLineService(user_line_dao,
                           user_dao,
                           line_dao,
                           validator,
                           notifier)
