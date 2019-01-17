# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class IncallScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, incall, schedule):
        self.validate_same_tenant(incall, schedule)
        self.validate_incall_not_already_associated(incall)

    def validate_same_tenant(self, incall, schedule):
        if incall.tenant_uuid != schedule.tenant_uuid:
            raise errors.different_tenants(
                incall_tenant_uuid=incall.tenant_uuid,
                schedule_tenant_uuid=schedule.tenant_uuid,
            )

    def validate_incall_not_already_associated(self, incall):
        if incall.schedules:
            raise errors.resource_associated(
                'Incall',
                'Schedule',
                incall_id=incall.id,
                schedule_id=incall.schedules[0].id
            )


def build_validator():
    return ValidationAssociation(
        association=[IncallScheduleAssociationValidator()],
    )
