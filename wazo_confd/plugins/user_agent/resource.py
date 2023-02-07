# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class UserAgentItem(ConfdResource):
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__()
        self.service = service
        self._middleware = middleware

    @required_acl('confd.users.{user_id}.agents.{agent_id}.update')
    def put(self, user_id, agent_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.associate(user_id, agent_id, tenant_uuids)
        return '', 204


class UserAgentList(ConfdResource):
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__()
        self.service = service
        self._middleware = middleware

    @required_acl('confd.users.{user_id}.agents.delete')
    def delete(self, user_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.dissociate(user_id, tenant_uuids)
        return '', 204
