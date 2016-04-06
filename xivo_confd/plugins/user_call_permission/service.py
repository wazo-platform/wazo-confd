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

from xivo_dao.resources.user_call_permission import dao as user_call_permission_dao
from xivo_confd.plugins.user_call_permission.notifier import build_notifier
from xivo_confd.plugins.user_call_permission.validator import build_validator


class UserCallPermissionService(object):

    def __init__(self, dao, validator, notifier):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier

    def find_all_by(self, **criteria):
        return self.dao.find_all_by(**criteria)

    def find_by(self, **criteria):
        return self.dao.find_by(**criteria)

    def get(self, user, call_permission):
        return self.dao.get_by(user_id=user.id, call_permission_id=call_permission.id)

    def associate(self, user, call_permission):
        self.validator.validate_association(user, call_permission)
        self.dao.associate(user, call_permission)
        self.notifier.associated(user, call_permission)

    def dissociate(self, user, call_permission):
        self.validator.validate_dissociation(user, call_permission)
        self.dao.get_by(user_id=user.id, call_permission_id=call_permission.id)
        self.dao.dissociate(user, call_permission)
        self.notifier.dissociated(user, call_permission)


def build_service():
    notifier = build_notifier()
    validator = build_validator()
    return UserCallPermissionService(user_call_permission_dao,
                                     validator,
                                     notifier)
