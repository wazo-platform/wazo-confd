# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class UserAgentItem(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, user_dao, agent_dao):
        super().__init__()
        self.service = service
        self.user_dao = user_dao
        self.agent_dao = agent_dao

    @required_acl('confd.users.{user_id}.agents.{agent_id}.update')
    def put(self, user_id, agent_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user = self.user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)
        agent = self.agent_dao.get(agent_id, tenant_uuids=tenant_uuids)
        self.service.associate(user, agent)
        return '', 204


class UserAgentList(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, user_dao):
        super().__init__()
        self.service = service
        self.user_dao = user_dao

    @required_acl('confd.users.{user_id}.agents.delete')
    def delete(self, user_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user = self.user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)
        self.service.dissociate(user)
        return '', 204
