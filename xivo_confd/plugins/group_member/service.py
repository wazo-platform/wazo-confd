# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.group import dao as group_dao_module

from .notifier import build_notifier
from .validator import build_validator_member_user, build_validator_member_extension


class GroupMemberUserService(object):

    def __init__(self, group_dao, notifier, validator_user, validator_extension):
        self.group_dao = group_dao
        self.validator_user = validator_user
        self.validator_extension = validator_extension
        self.notifier = notifier

    def associate_all_users(self, group, members):
        users = [member['user'] for member in members]
        self.validator_user.validate_association(group, users)
        self.group_dao.associate_all_member_users(group, members)
        self.notifier.users_associated(group, users)

    def associate_all_extensions(self, group, members):
        extensions = [member['extension'] for member in members]
        self.validator_extension.validate_association(group, extensions)
        self.group_dao.associate_all_member_extensions(group, members)
        self.notifier.extensions_associated(group, extensions)


def build_service():
    return GroupMemberUserService(group_dao_module,
                                  build_notifier(),
                                  build_validator_member_user(),
                                  build_validator_member_extension())
