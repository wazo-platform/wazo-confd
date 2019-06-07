# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.queue import dao as queue_dao

from xivo_confd.helpers.validator import (Optional,
                                          UniqueField,
                                          UniqueFieldChanged,
                                          Validator,
                                          ValidationGroup)


class GroupValidator(Validator):

    def validate(self, group):
        self.validate_unique_name_through_queue(group)

    def validate_unique_name_through_queue(self, group):
        queue = queue_dao.find_by(name=group.name)
        if queue is not None:
            raise errors.resource_exists('Queue', name=group.name)


def build_validator():
    return ValidationGroup(
        create=[
            UniqueField('name',
                        lambda name: group_dao.find_by(name=name),
                        'Group'),
            GroupValidator(),
        ],
        edit=[
            Optional('name',
                     UniqueFieldChanged('name', group_dao, 'Group')),
            GroupValidator(),
        ]
    )
