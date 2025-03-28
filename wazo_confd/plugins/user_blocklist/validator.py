# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.blocklist import BlocklistNumber
from xivo_dao.helpers import errors
from xivo_dao.resources.blocklist import dao

from wazo_confd.helpers.validator import ValidationGroup, Validator


class UniqueNumberInBlocklist(Validator):
    def __init__(self, dao, update=False):
        super().__init__()
        self.dao = dao
        self.update = update

    def validate(self, model: BlocklistNumber):
        existing = self.dao.find_by(
            number=model.number, blocklist_uuid=model.blocklist_uuid
        )
        if not existing:
            return
        if self.update and existing.uuid == model.uuid:
            return
        raise errors.resource_exists(
            'BlocklistNumber',
            number=model.number,
            blocklist_uuid=model.blocklist_uuid,
        )


def build_validator():
    return ValidationGroup(
        create=[UniqueNumberInBlocklist(dao)],
        edit=[UniqueNumberInBlocklist(dao, update=True)],
    )
