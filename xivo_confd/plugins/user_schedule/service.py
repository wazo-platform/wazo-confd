# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .notifier import build_notifier
from .validator import build_validator


class UserScheduleService(object):

    def __init__(self, notifier, validator):
        self.validator = validator
        self.notifier = notifier

    def associate(self, user, schedule):
        if schedule in user.schedules:
            return

        self.validator.validate_association(user, schedule)
        user.schedules = [schedule]
        self.notifier.associated(user, schedule)

    def dissociate(self, user, schedule):
        if schedule not in user.schedules:
            return

        self.validator.validate_dissociation(user, schedule)
        user.schedules = []
        self.notifier.dissociated(user, schedule)


def build_service():
    return UserScheduleService(build_notifier(),
                               build_validator())
