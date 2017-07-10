# -*- coding: UTF-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.helpers import errors
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_confd.plugins.user_line import notifier
from xivo_confd.plugins.user_line.validator import build_validator


class UserLineService(object):

    def __init__(self, dao, validator, notifier):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier

    def find_all_by(self, **criteria):
        return self.dao.find_all_by(**criteria)

    def find_by(self, **criteria):
        return self.dao.find_by(**criteria)

    def get(self, user, line):
        return self.dao.get_by(user_id=user.id, line_id=line.id)

    def associate(self, user, line):
        self.validator.validate_association(user, line)
        user_line = self.dao.associate(user, line)
        self.notifier.associated(user_line)
        return user_line

    def dissociate(self, user, line):
        self.validator.validate_dissociation(user, line)
        user_line = self.dao.get_by(user_id=user.id, line_id=line.id)
        self.notifier.dissociated(user_line)
        self.dao.dissociate(user, line)

    def associate_all_lines(self, user, lines):
        if len(lines) != len(set(lines)):
            raise errors.not_permitted('Cannot associate same line more than once')

        for existing_line in user.lines:
            if existing_line not in lines:
                self.validator.validate_dissociation(user, existing_line)

        for line in lines:
            if line not in user.lines:
                self.validator.validate_association(user, line)

        for existing_line in user.lines:
            if existing_line not in lines:
                user_line = self.find_by(user_id=user.id, line_id=existing_line.id)
                self.notifier.dissociated(user_line)

        user_lines = self.dao.associate_all_lines(user, lines)

        for user_line in user_lines:
            self.notifier.associated(user_line)


def build_service():
    validator = build_validator()
    return UserLineService(user_line_dao,
                           validator,
                           notifier)
