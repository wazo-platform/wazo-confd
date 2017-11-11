# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class UserScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, user, schedule):
        self.validate_user_not_already_associated(user)

    def validate_user_not_already_associated(self, user):
        if user.schedules:
            raise errors.resource_associated('User', 'Schedule',
                                             user_id=user.id,
                                             schedule_id=user.schedules[0].id)


class UserScheduleDissociationValidator(ValidatorAssociation):

    def validate(self, user, schedule):
        self.validate_user_schedule_exists(user, schedule)

    def validate_user_schedule_exists(self, user, schedule):
        if user not in schedule.users:
            raise errors.not_found('UserSchedule',
                                   user_id=user.id,
                                   schedule_id=schedule.id)


def build_validator():
    return ValidationAssociation(
        association=[UserScheduleAssociationValidator()],
        dissociation=[UserScheduleDissociationValidator()]
    )
