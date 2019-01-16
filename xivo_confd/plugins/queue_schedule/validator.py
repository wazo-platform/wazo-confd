# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class QueueScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, queue, schedule):
        self.validate_queue_not_already_associated(queue)

    def validate_queue_not_already_associated(self, queue):
        if queue.schedules:
            raise errors.resource_associated('Queue', 'Schedule',
                                             queue_id=queue.id,
                                             schedule_id=queue.schedules[0].id)


def build_validator():
    return ValidationAssociation(
        association=[QueueScheduleAssociationValidator()],
    )
