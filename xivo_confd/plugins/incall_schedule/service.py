# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .notifier import build_notifier
from .validator import build_validator


class IncallScheduleService:

    def __init__(self, notifier, validator):
        self.validator = validator
        self.notifier = notifier

    def associate(self, incall, schedule):
        if schedule in incall.schedules:
            return

        self.validator.validate_association(incall, schedule)
        incall.schedules = [schedule]
        self.notifier.associated(incall, schedule)

    def dissociate(self, incall, schedule):
        if schedule not in incall.schedules:
            return

        self.validator.validate_dissociation(incall, schedule)
        incall.schedules = []
        self.notifier.dissociated(incall, schedule)


def build_service():
    return IncallScheduleService(build_notifier(),
                                 build_validator())
