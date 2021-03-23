# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.queue import dao as queue_dao

from wazo_confd.helpers.validator import (
    Validator,
    ValidationGroup,
)


class GroupValidator(Validator):
    def validate(self, group):
        self.validate_unique_name_through_queue(group)

    # TODO(pc-m): remove this validation once queues get there name generated
    def validate_unique_name_through_queue(self, group):
        queue = queue_dao.find_by(name=group.name)
        if queue is not None:
            raise errors.resource_exists('Queue', name=group.name)


def build_validator():
    return ValidationGroup(create=[GroupValidator()])
