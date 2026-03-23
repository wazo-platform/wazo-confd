# Copyright 2025-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import logging

from xivo_dao.alchemy.blocklist import Blocklist
from xivo_dao.alchemy.blocklist_number import BlocklistNumber
from xivo_dao.helpers.errors import NotFoundError
from xivo_dao.resources.blocklist import dao
from xivo_dao.resources.user import dao as user_dao

from wazo_confd.helpers.resource import CRUDService

from .notifier import build_notifier
from .validator import build_validator

logger = logging.getLogger(__name__)


class UserBlocklistService(CRUDService):
    def __init__(self, dao, validator, notifier, user_dao):
        super().__init__(dao, validator, notifier)
        self.user_dao = user_dao

    def find_all_by(self, **criteria) -> list[BlocklistNumber]:
        return self.dao.find_all_by(**criteria)

    def get_or_create_user_blocklist(self, user_uuid: str) -> Blocklist:
        try:
            return self.dao.get_blocklist_by(user_uuid=user_uuid)
        except NotFoundError:
            logger.debug('Creating blocklist for user %s', user_uuid)
            user = self.user_dao.get_by(uuid=user_uuid)
            return self.dao.create_blocklist(
                Blocklist(user_uuid=user_uuid, tenant_uuid=user.tenant_uuid)
            )


def build_service():
    return UserBlocklistService(dao, build_validator(), build_notifier(), user_dao)
