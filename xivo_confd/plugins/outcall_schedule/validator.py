# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class OutcallScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, outcall, schedule):
        self.validate_same_tenant(outcall, schedule)
        self.validate_outcall_not_already_associated(outcall)

    def validate_same_tenant(self, outcall, schedule):
        if outcall.tenant_uuid != schedule.tenant_uuid:
            raise errors.different_tenants(
                outcall_tenant_uuid=outcall.tenant_uuid,
                schedule_tenant_uuid=schedule.tenant_uuid,
            )

    def validate_outcall_not_already_associated(self, outcall):
        if outcall.schedules:
            raise errors.resource_associated(
                'Outcall',
                'Schedule',
                outcall_id=outcall.id,
                schedule_id=outcall.schedules[0].id,
            )


def build_validator():
    return ValidationAssociation(
        association=[OutcallScheduleAssociationValidator()],
    )
