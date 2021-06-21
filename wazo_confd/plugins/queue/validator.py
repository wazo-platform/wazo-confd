# Copyright 2018-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.queue import dao as queue_dao

from wazo_confd.helpers.validator import (
    Optional,
    UniqueField,
    UniqueFieldChanged,
    ValidationGroup,
    Validator,
)
from wazo_confd.helpers.destination import DestinationValidator


class QueueValidator(Validator):
    def validate(self, queue):
        self.validate_unique_name_through_group(queue)

    def validate_unique_name_through_group(self, queue):
        group = group_dao.find_by(name=queue.name)
        if group is not None:
            raise errors.resource_exists('Group', name=group.name)


class WaitDestinationValidator(DestinationValidator):
    def validate(self, queue):
        wait_time_destination = queue.wait_time_destination
        if wait_time_destination:
            super().validate(wait_time_destination)

        wait_ratio_destination = queue.wait_ratio_destination
        if wait_ratio_destination:
            super().validate(wait_ratio_destination)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('name', lambda name: queue_dao.find_by(name=name), 'Queue'),
            QueueValidator(),
            WaitDestinationValidator(),
        ],
        edit=[
            Optional('name', UniqueFieldChanged('name', queue_dao.find_by, 'Queue')),
            QueueValidator(),
            WaitDestinationValidator(),
        ],
    )
