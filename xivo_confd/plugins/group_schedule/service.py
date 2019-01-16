# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .notifier import build_notifier
from .validator import build_validator


class GroupScheduleService(object):

    def __init__(self, notifier, validator):
        self.validator = validator
        self.notifier = notifier

    def associate(self, group, schedule):
        if schedule in group.schedules:
            return

        self.validator.validate_association(group, schedule)
        group.schedules = [schedule]
        self.notifier.associated(group, schedule)

    def dissociate(self, group, schedule):
        if schedule not in group.schedules:
            return

        self.validator.validate_dissociation(group, schedule)
        group.schedules = []
        self.notifier.dissociated(group, schedule)


def build_service():
    return GroupScheduleService(build_notifier(),
                                build_validator())
