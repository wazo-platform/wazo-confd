# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.resources.moh import dao as moh_dao
from xivo_dao.resources.queue import dao as queue_dao

from wazo_confd.helpers.validator import MOHExists, ValidationGroup, Validator


class GroupValidator(Validator):
    def validate(self, group):
        self.validate_unique_name_through_queue(group)

    # TODO(pc-m): remove this validation once queues get there name generated
    def validate_unique_name_through_queue(self, group):
        queue = queue_dao.find_by(name=group.name)
        if queue is not None:
            raise errors.resource_exists('Queue', name=group.name)


def build_validator():
    moh_validator = MOHExists('music_on_hold', moh_dao.get_by)
    return ValidationGroup(
        create=[GroupValidator(), moh_validator], edit=[moh_validator]
    )
