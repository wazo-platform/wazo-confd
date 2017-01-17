# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import ValidatorAssociation, ValidationAssociation


class IncallScheduleAssociationValidator(ValidatorAssociation):

    def validate(self, incall, schedule):
        self.validate_incall_not_already_associated(incall)

    def validate_incall_not_already_associated(self, incall):
        if incall.schedules:
            raise errors.resource_associated('Incall', 'Schedule',
                                             incall_id=incall.id,
                                             schedule_id=incall.schedules[0].id)


class IncallScheduleDissociationValidator(ValidatorAssociation):

    def validate(self, incall, schedule):
        self.validate_incall_schedule_exists(incall, schedule)

    def validate_incall_schedule_exists(self, incall, schedule):
        if incall not in schedule.incalls:
            raise errors.not_found('IncallSchedule',
                                   incall_id=incall.id,
                                   schedule_id=schedule.id)


def build_validator():
    return ValidationAssociation(
        association=[IncallScheduleAssociationValidator()],
        dissociation=[IncallScheduleDissociationValidator()]
    )
