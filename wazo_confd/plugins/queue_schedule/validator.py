# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from wazo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class QueueScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, queue, schedule):
        self.validate_same_tenant(queue, schedule)
        self.validate_queue_not_already_associated(queue)

    def validate_same_tenant(self, queue, schedule):
        if queue.tenant_uuid != schedule.tenant_uuid:
            raise errors.different_tenants(
                queue_tenant_uuid=queue.tenant_uuid,
                schedule_tenant_uuid=schedule.tenant_uuid,
            )

    def validate_queue_not_already_associated(self, queue):
        if queue.schedules:
            raise errors.resource_associated('Queue', 'Schedule',
                                             queue_id=queue.id,
                                             schedule_id=queue.schedules[0].id)


def build_validator():
    return ValidationAssociation(
        association=[QueueScheduleAssociationValidator()],
    )
