# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request
from marshmallow import fields
from marshmallow.validate import Range

from xivo_dao.alchemy.agentqueueskill import AgentQueueSkill

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource
from xivo_confd.helpers.mallow import BaseSchema


class AgentSkillSchema(BaseSchema):
    skill_weight = fields.Integer(validate=Range(min=0), missing=0, attribute='weight')


class AgentSkillItem(ConfdResource):

    schema = AgentSkillSchema

    def __init__(self, service, agent_dao, skill_dao):
        super(AgentSkillItem, self).__init__()
        self.service = service
        self.agent_dao = agent_dao
        self.skill_dao = skill_dao

    @required_acl('confd.agents.{agent_id}.skills.{skill_id}.update')
    def put(self, agent_id, skill_id):
        agent = self.agent_dao.get(agent_id)
        skill = self.skill_dao.get(skill_id)
        agent_skill = self._find_or_create_agent_skill(agent, skill)
        form = self.schema().load(request.get_json()).data
        agent_skill.weight = form['weight']
        self.service.associate_agent_skill(agent, agent_skill)
        return '', 204

    @required_acl('confd.agents.{agent_id}.skills.{skill_id}.delete')
    def delete(self, agent_id, skill_id):
        agent = self.agent_dao.get(agent_id)
        skill = self.skill_dao.get(skill_id)
        agent_skill = self._find_or_create_agent_skill(agent, skill)
        self.service.dissociate_agent_skill(agent, agent_skill)
        return '', 204

    def _find_or_create_agent_skill(self, agent, skill):
        agent_skill = self.service.find_agent_skill(agent, skill)
        if not agent_skill:
            agent_skill = AgentQueueSkill(skill=skill)
        return agent_skill
