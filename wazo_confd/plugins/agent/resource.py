# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import AgentSchema, AgentSchemaPUT


class AgentList(ListResource):

    model = Agent
    schema = AgentSchema

    def build_headers(self, agent):
        return {'Location': url_for('agents', id=agent.id, _external=True)}

    @required_acl('confd.agents.create')
    def post(self):
        return super().post()

    @required_acl('confd.agents.read')
    def get(self):
        return super().get()


class AgentItem(ItemResource):

    schema = AgentSchemaPUT
    has_tenant_uuid = True

    @required_acl('confd.agents.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.agents.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.agents.{id}.delete')
    def delete(self, id):
        return super().delete(id)
