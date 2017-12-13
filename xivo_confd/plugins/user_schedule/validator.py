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


def build_validator():
    return ValidationAssociation(
        association=[UserScheduleAssociationValidator()],
    )
