# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.outcall import dao as outcall_dao_module

from .notifier import build_notifier
from .validator import build_validator


class OutcallCallPermissionService(object):

    def __init__(self, outcall_dao, validator, notifier):
        self.outcall_dao = outcall_dao
        self.validator = validator
        self.notifier = notifier

    def associate(self, outcall, call_permission):
        self.validator.validate_association(outcall, call_permission)
        self.outcall_dao.associate_call_permission(outcall, call_permission)
        self.notifier.associated(outcall, call_permission)

    def dissociate(self, outcall, call_permission):
        self.validator.validate_dissociation(outcall, call_permission)
        self.outcall_dao.dissociate_call_permission(outcall, call_permission)
        self.notifier.dissociated(outcall, call_permission)


def build_service():
    return OutcallCallPermissionService(outcall_dao_module,
                                        build_validator(),
                                        build_notifier())
