# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent
from .schema import AgentSchema


class AgentMiddleWare:
    def __init__(self, service):
        self._service = service
        self._schema = AgentSchema()

    def create(self, body, tenant_uuid):
        form = self._schema.load(body)
        form['tenant_uuid'] = tenant_uuid
        model = Agent(**form)
        model = self._service.create(model)
        return self._schema.dump(model)

    def delete(self, user_id, tenant_uuids):
        agent = self._service.get(user_id, tenant_uuids=tenant_uuids)
        self._service.delete(agent)
