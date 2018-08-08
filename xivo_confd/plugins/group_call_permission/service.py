# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.group import dao as group_dao_module

from .notifier import build_notifier
from .validator import build_validator


class GroupCallPermissionService(object):

    def __init__(self, group_dao, notifier, validator):
        self.group_dao = group_dao
        self.notifier = notifier
        self.validator = validator

    def associate(self, group, call_permission):
        if call_permission in group.call_permissions:
            return

        self.validator.validate_association(group, call_permission)
        self.group_dao.associate_call_permission(group, call_permission)
        self.notifier.associated(group, call_permission)

    def dissociate(self, group, call_permission):
        if call_permission not in group.call_permissions:
            return

        self.group_dao.dissociate_call_permission(group, call_permission)
        self.notifier.dissociated(group, call_permission)


def build_service():
    return GroupCallPermissionService(
        group_dao_module,
        build_notifier(),
        build_validator(),
    )
