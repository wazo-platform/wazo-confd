# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for
from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource, build_tenant

from .schema import AgentSchema, AgentSchemaPUT


class AgentList(ListResource):
    model = Agent
    schema = AgentSchema

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    def build_headers(self, agent):
        return {'Location': url_for('agents', id=agent['id'], _external=True)}

    @required_acl('confd.agents.create')
    def post(self):
        tenant_uuid = build_tenant()
        tenant_uuids = self._build_tenant_list({'recurse': True})
        resource = self._middleware.create(
            request.get_json(), tenant_uuid, tenant_uuids
        )
        return resource, 201, self.build_headers(resource)

    @required_acl('confd.agents.read')
    def get(self):
        return super().get()


class AgentItem(ItemResource):
    schema = AgentSchemaPUT
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    @required_acl('confd.agents.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.agents.{id}.update')
    def put(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.update(id, request.get_json(), tenant_uuids)
        return '', 204

    @required_acl('confd.agents.{id}.delete')
    def delete(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.delete(id, tenant_uuids)
        return '', 204
