# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.resources.agent import dao as agent_dao_module
from xivo_dao.resources.queue import dao as queue_dao_module

from .notifier import build_notifier


class QueueMemberService(object):

    def __init__(self, queue_dao, agent_dao, notifier):
        self.queue_dao = queue_dao
        self.agent_dao = agent_dao
        self.notifier = notifier

    def get(self, queue, agent):
        member = self.find(queue, agent)
        if not member:
            raise errors.not_found('QueueMember', agent_id=agent.id, queue_id=queue.id)
        return member

    def get_agent(self, agent_id):
        agent = self.agent_dao.find(agent_id)
        if not agent:
            raise errors.param_not_found('agent_id', 'Agent')
        return agent

    def find(self, queue, agent):
        for member in queue.agent_queue_members:
            if member.agent == agent:
                return member
        return None

    def edit(self, queue, member):
        self.queue_dao.edit(queue)
        self.notifier.edited(queue, member)

    def associate_legacy(self, queue, member):
        if member in queue.agent_queue_members:
            raise errors.resource_associated('Agent', 'Queue', member.agent.id, queue.id)
        self.queue_dao.associate_member_agent(queue, member)
        self.notifier.associated(queue, member)

    def dissociate_member_agent(self, queue, member):
        self.queue_dao.dissociate_member_agent(queue, member)
        self.notifier.dissociated(queue, member)


def build_service():
    return QueueMemberService(
        queue_dao_module,
        agent_dao_module,
        build_notifier(),
    )
