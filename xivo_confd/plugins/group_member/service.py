# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.group import dao as group_dao_module

from .notifier import build_notifier
from .validator import build_validator_member_user, build_validator_member_extension


class GroupMemberUserService:

    def __init__(self, group_dao, notifier, validator_user, validator_extension):
        self.group_dao = group_dao
        self.validator_user = validator_user
        self.validator_extension = validator_extension
        self.notifier = notifier

    def find_member_user(self, queue, user):
        for member in queue.user_queue_members:
            if member.user == user:
                return member
        return None

    def find_member_extension(self, queue, extension):
        for member in queue.extension_queue_members:
            if member.extension.exten == extension.exten and member.extension.context == extension.context:
                return member
        return None

    def associate_all_users(self, group, members):
        self.validator_user.validate_association(group, members)
        self.group_dao.associate_all_member_users(group, members)
        self.notifier.users_associated(group, members)

    def associate_all_extensions(self, group, members):
        self.validator_extension.validate_association(group, members)
        self.group_dao.associate_all_member_extensions(group, members)
        self.notifier.extensions_associated(group, members)


def build_service():
    return GroupMemberUserService(
        group_dao_module,
        build_notifier(),
        build_validator_member_user(),
        build_validator_member_extension()
    )
