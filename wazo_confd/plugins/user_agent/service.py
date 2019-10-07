# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao

from wazo_confd.plugins.user_agent.notifier import build_notifier
from wazo_confd.plugins.user_agent.validator import build_validator


class UserAgentService:
    def __init__(self, dao, validator, notifier):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier

    def find_by_user_id(self, user_id, tenant_uuids=None):
        return self.dao.find_by_id_uuid(user_id, tenant_uuids=tenant_uuids)

    def associate(self, user, agent):
        if agent.id == user.agent_id:
            return

        self.validator.validate_association(user, agent)
        user.agent_id = agent.id
        self.dao.edit(user)
        self.notifier.associated(user, agent)

    def dissociate(self, user):
        agent = user.agent
        if not agent:
            return

        self.validator.validate_dissociation(user, agent)
        user.agent_id = None
        self.dao.edit(user)
        self.notifier.dissociated(user, agent)


def build_service():
    return UserAgentService(user_dao, build_validator(), build_notifier())
