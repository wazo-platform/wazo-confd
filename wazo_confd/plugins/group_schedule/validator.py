# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from wazo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class GroupScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, group, schedule):
        self.validate_same_tenant(group, schedule)
        self.validate_group_not_already_associated(group)

    def validate_same_tenant(self, group, schedule):
        if group.tenant_uuid != schedule.tenant_uuid:
            raise errors.different_tenants(
                group_tenant_uuid=group.tenant_uuid,
                schedule_tenant_uuid=schedule.tenant_uuid,
            )

    def validate_group_not_already_associated(self, group):
        if group.schedules:
            raise errors.resource_associated('Group', 'Schedule',
                                             group_id=group.id,
                                             schedule_id=group.schedules[0].id)


def build_validator():
    return ValidationAssociation(
        association=[GroupScheduleAssociationValidator()],
    )
