# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class IncallScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, incall, schedule):
        if schedule in incall.schedules:
            return
        self.validate_incall_not_already_associated(incall)

    def validate_incall_not_already_associated(self, incall):
        if incall.schedules:
            raise errors.resource_associated('Incall', 'Schedule',
                                             incall_id=incall.id,
                                             schedule_id=incall.schedules[0].id)


def build_validator():
    return ValidationAssociation(
        association=[IncallScheduleAssociationValidator()],
    )
