# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class IncallScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, incall, schedule):
        self.validate_incall_not_already_associated(incall)

    def validate_incall_not_already_associated(self, incall):
        if incall.schedules:
            raise errors.resource_associated('Incall', 'Schedule',
                                             incall_id=incall.id,
                                             schedule_id=incall.schedules[0].id)


class IncallScheduleDissociationValidator(ValidatorAssociation):

    def validate(self, incall, schedule):
        self.validate_incall_schedule_exists(incall, schedule)

    def validate_incall_schedule_exists(self, incall, schedule):
        if incall not in schedule.incalls:
            raise errors.not_found('IncallSchedule',
                                   incall_id=incall.id,
                                   schedule_id=schedule.id)


def build_validator():
    return ValidationAssociation(
        association=[IncallScheduleAssociationValidator()],
        dissociation=[IncallScheduleDissociationValidator()]
    )
