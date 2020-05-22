# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import fields
from marshmallow.validate import Range

from xivo_dao.alchemy.agentqueueskill import AgentQueueSkill

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource
from wazo_confd.helpers.mallow import BaseSchema


class AgentSkillSchema(BaseSchema):
    skill_weight = fields.Integer(validate=Range(min=0), missing=0, attribute='weight')


class AgentSkillItem(ConfdResource):

    schema = AgentSkillSchema
    has_tenant_uuid = True

    def __init__(self, service, agent_dao, skill_dao):
        super().__init__()
        self.service = service
        self.agent_dao = agent_dao
        self.skill_dao = skill_dao

    @required_acl('confd.agents.{agent_id}.skills.{skill_id}.update')
    def put(self, agent_id, skill_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        agent = self.agent_dao.get(agent_id, tenant_uuids=tenant_uuids)
        skill = self.skill_dao.get(skill_id, tenant_uuids=tenant_uuids)
        agent_skill = self._find_or_create_agent_skill(agent, skill)
        form = self.schema().load(request.get_json())
        agent_skill.weight = form['weight']
        self.service.associate_agent_skill(agent, agent_skill)
        return '', 204

    @required_acl('confd.agents.{agent_id}.skills.{skill_id}.delete')
    def delete(self, agent_id, skill_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        agent = self.agent_dao.get(agent_id, tenant_uuids=tenant_uuids)
        skill = self.skill_dao.get(skill_id, tenant_uuids=tenant_uuids)
        agent_skill = self._find_or_create_agent_skill(agent, skill)
        self.service.dissociate_agent_skill(agent, agent_skill)
        return '', 204

    def _find_or_create_agent_skill(self, agent, skill):
        agent_skill = self.service.find_agent_skill(agent, skill)
        if not agent_skill:
            agent_skill = AgentQueueSkill(skill=skill)
        return agent_skill
