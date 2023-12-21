# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.agent import dao as agent_dao
from xivo_dao.resources.user import dao as user_dao


class UserAgentAssociationMiddleWare:
    def __init__(self, service):
        self._service = service

    def associate(self, user_id, agent_id, tenant_uuids):
        user = user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)
        agent = agent_dao.get(agent_id, tenant_uuids=tenant_uuids)
        self._service.associate(user, agent)

    def dissociate(self, user_id, tenant_uuids):
        user = user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)
        self._service.dissociate(user)
