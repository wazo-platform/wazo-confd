# -*- coding: UTF-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.call_pickup import dao as call_pickup_dao_module

from .notifier import build_notifier
from .validator import (
    build_validator_interceptor_user,
    build_validator_target_user,
)


class CallPickupUserService(object):

    def __init__(self, call_pickup_dao, notifier, validator_interceptor_user, validator_target_user):
        self.call_pickup_dao = call_pickup_dao
        self.notifier = notifier
        self.validator_interceptor_user = validator_interceptor_user
        self.validator_target_user = validator_target_user

    def associate_interceptor_users(self, call_pickup, users):
        self.validator_interceptor_user.validate_association(call_pickup, users)
        self.call_pickup_dao.associate_interceptor_users(call_pickup, users)
        self.notifier.interceptor_users_associated(call_pickup, users)

    def associate_target_users(self, call_pickup, users):
        self.validator_target_user.validate_association(call_pickup, users)
        self.call_pickup_dao.associate_target_users(call_pickup, users)
        self.notifier.target_users_associated(call_pickup, users)


def build_service():
    return CallPickupUserService(
        call_pickup_dao_module,
        build_notifier(),
        build_validator_interceptor_user(),
        build_validator_target_user(),
    )
