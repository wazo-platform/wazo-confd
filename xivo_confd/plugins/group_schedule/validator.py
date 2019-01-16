# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class GroupScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, group, schedule):
        self.validate_group_not_already_associated(group)

    def validate_group_not_already_associated(self, group):
        if group.schedules:
            raise errors.resource_associated('Group', 'Schedule',
                                             group_id=group.id,
                                             schedule_id=group.schedules[0].id)


def build_validator():
    return ValidationAssociation(
        association=[GroupScheduleAssociationValidator()],
    )
