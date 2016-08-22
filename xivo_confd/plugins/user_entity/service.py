# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_confd.plugins.user_entity.notifier import build_notifier
from xivo_confd.plugins.user_entity.validator import build_validator


class UserEntityService(object):

    def __init__(self, dao, validator, notifier):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier

    def find_by_user_id(self, user_id):
        user = self.dao.find_by(id=user_id)
        user.user_id = user_id
        return user

    def associate(self, user, entity):
        self.validator.validate_association(user, entity)
        user.entity_id = entity.id
        self.dao.edit(user)
        self.notifier.associated(user, entity)


def build_service():
    return UserEntityService(user_dao,
                             build_validator(),
                             build_notifier())
