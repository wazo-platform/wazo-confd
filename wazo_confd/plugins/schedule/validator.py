# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.helpers.destination import DestinationValidator
from wazo_confd.helpers.validator import Validator, ValidationGroup


class ScheduleModelValidator(Validator):
    def __init__(self, destination_validator):
        self._destination_validator = destination_validator

    def validate(self, schedule):
        self._destination_validator.validate(schedule.closed_destination)


def build_validator():
    schedule_validator = ScheduleModelValidator(DestinationValidator())
    return ValidationGroup(create=[schedule_validator], edit=[schedule_validator])
