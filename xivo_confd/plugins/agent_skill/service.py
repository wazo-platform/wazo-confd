# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.agent import dao as agent_dao_module
from xivo_dao.resources.skill import dao as skill_dao_module

from .notifier import build_notifier


class AgentMemberService(object):

    def __init__(self, agent_dao, skill_dao, notifier):
        self.agent_dao = agent_dao
        self.skill_dao = skill_dao
        self.notifier = notifier

    def find_agent_skill(self, agent, skill):
        for agent_skill in agent.agent_queue_skills:
            if agent_skill.skill == skill:
                return agent_skill
        return None

    def associate_agent_skill(self, agent, agent_skill):
        if agent_skill in agent.agent_queue_skills:
            return

        self.agent_dao.associate_agent_skill(agent, agent_skill)
        self.notifier.skill_associated(agent, agent_skill)

    def dissociate_agent_skill(self, agent, agent_skill):
        if agent_skill not in agent.agent_queue_skills:
            return

        self.agent_dao.dissociate_agent_skill(agent, agent_skill)
        self.notifier.skill_dissociated(agent, agent_skill)


def build_service():
    return AgentMemberService(
        agent_dao_module,
        skill_dao_module,
        build_notifier(),
    )
