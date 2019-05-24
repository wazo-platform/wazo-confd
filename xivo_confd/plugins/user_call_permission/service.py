# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user_call_permission import dao as user_call_permission_dao

from .notifier import build_notifier
from .validator import build_validator


class UserCallPermissionService:

    def __init__(self, dao, notifier, validator):
        self.dao = dao
        self.notifier = notifier
        self.validator = validator

    def find_all_by(self, **criteria):
        return self.dao.find_all_by(**criteria)

    def find_by(self, **criteria):
        return self.dao.find_by(**criteria)

    def get(self, user, call_permission):
        return self.dao.get_by(user_id=user.id, call_permission_id=call_permission.id)

    def associate(self, user, call_permission):
        if self.dao.find_by(user_id=user.id, call_permission_id=call_permission.id):
            return

        self.validator.validate_association(user, call_permission)
        self.dao.associate(user, call_permission)
        self.notifier.associated(user, call_permission)

    def dissociate(self, user, call_permission):
        if not self.dao.find_by(user_id=user.id, call_permission_id=call_permission.id):
            return

        self.dao.dissociate(user, call_permission)
        self.notifier.dissociated(user, call_permission)

    def dissociate_all_by_user(self, user):
        self.dao.dissociate_all_by_user(user)


def build_service():
    return UserCallPermissionService(
        user_call_permission_dao,
        build_notifier(),
        build_validator(),
    )
