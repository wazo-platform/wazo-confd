# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.group import dao as group_dao_module

from .notifier import build_notifier


class GroupCallPermissionService(object):

    def __init__(self, group_dao, notifier):
        self.group_dao = group_dao
        self.notifier = notifier

    def associate(self, group, call_permission):
        self.group_dao.associate_call_permission(group, call_permission)
        self.notifier.associated(group, call_permission)

    def dissociate(self, group, call_permission):
        self.group_dao.dissociate_call_permission(group, call_permission)
        self.notifier.dissociated(group, call_permission)


def build_service():
    return GroupCallPermissionService(group_dao_module,
                                      build_notifier())
