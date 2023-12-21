# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent

from ...middleware import ResourceMiddleware
from .schema import AgentSchema, AgentSchemaPUT


class AgentMiddleWare(ResourceMiddleware):
    def __init__(self, service, middleware_handle):
        self._service = service
        self._schema = AgentSchema()
        self._update_schema = AgentSchemaPUT()
        self._middleware_handle = middleware_handle

    def create(self, body, tenant_uuid, tenant_uuids):
        queues = body.pop('queues', None) or []

        form = self._schema.load(body)
        form['tenant_uuid'] = tenant_uuid
        model = Agent(**form)
        model = self._service.create(model)

        queue_member_middleware = self._middleware_handle.get('queue_member')
        for queue in queues:
            queue_member_middleware.associate(
                queue, queue['id'], model.id, tenant_uuids
            )

        return self._schema.dump(model)

    def delete(self, user_id, tenant_uuids):
        agent = self._service.get(user_id, tenant_uuids=tenant_uuids)
        self._service.delete(agent)

    def update(self, agent_id, body, tenant_uuids):
        model = self._service.get(agent_id, tenant_uuids=tenant_uuids)
        self.parse_and_update(model, body)
