# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
