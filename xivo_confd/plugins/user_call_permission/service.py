# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

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
        self.dao.dissociate(user, call_permission)
        self.notifier.dissociated(user, call_permission)

    def dissociate_all_by_user(self, user):
        self.dao.dissociate_all_by_user(user)


def build_service():
    notifier = build_notifier()
    validator = build_validator()
    return UserCallPermissionService(user_call_permission_dao,
                                     validator,
                                     notifier)
