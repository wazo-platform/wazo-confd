# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class OutcallScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, outcall, schedule):
        self.validate_outcall_not_already_associated(outcall)

    def validate_outcall_not_already_associated(self, outcall):
        if outcall.schedules:
            raise errors.resource_associated('Outcall', 'Schedule',
                                             outcall_id=outcall.id,
                                             schedule_id=outcall.schedules[0].id)


class OutcallScheduleDissociationValidator(ValidatorAssociation):

    def validate(self, outcall, schedule):
        self.validate_outcall_schedule_exists(outcall, schedule)

    def validate_outcall_schedule_exists(self, outcall, schedule):
        if outcall not in schedule.outcalls:
            raise errors.not_found('OutcallSchedule',
                                   outcall_id=outcall.id,
                                   schedule_id=schedule.id)


def build_validator():
    return ValidationAssociation(
        association=[OutcallScheduleAssociationValidator()],
        dissociation=[OutcallScheduleDissociationValidator()]
    )
