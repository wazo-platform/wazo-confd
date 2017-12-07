# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class OutcallScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, outcall, schedule):
        if schedule in outcall.schedules:
            return
        self.validate_outcall_not_already_associated(outcall)

    def validate_outcall_not_already_associated(self, outcall):
        if outcall.schedules:
            raise errors.resource_associated('Outcall', 'Schedule',
                                             outcall_id=outcall.id,
                                             schedule_id=outcall.schedules[0].id)


def build_validator():
    return ValidationAssociation(
        association=[OutcallScheduleAssociationValidator()],
    )
