# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.outcall import dao as outcall_dao_module

from .notifier import build_notifier


class OutcallCallPermissionService(object):

    def __init__(self, outcall_dao, notifier):
        self.outcall_dao = outcall_dao
        self.notifier = notifier

    def associate(self, outcall, call_permission):
        if call_permission in outcall.call_permissions:
            return

        self.outcall_dao.associate_call_permission(outcall, call_permission)
        self.notifier.associated(outcall, call_permission)

    def dissociate(self, outcall, call_permission):
        if call_permission not in outcall.call_permissions:
            return

        self.outcall_dao.dissociate_call_permission(outcall, call_permission)
        self.notifier.dissociated(outcall, call_permission)


def build_service():
    return OutcallCallPermissionService(outcall_dao_module,
                                        build_notifier())
