# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors
from xivo_dao.resources.agent import dao as agent_dao_module
from xivo_dao.resources.queue import dao as queue_dao_module

from .notifier import build_notifier
from .validator import build_validator_member_user


class QueueMemberService(object):

    def __init__(self, queue_dao, agent_dao, validator_member_user, notifier):
        self.queue_dao = queue_dao
        self.agent_dao = agent_dao
        self.notifier = notifier
        self.validator_member_user = validator_member_user

    def get_member_agent(self, queue, agent):
        member = self.find_member_agent(queue, agent)
        if not member:
            raise errors.not_found('QueueMember', agent_id=agent.id, queue_id=queue.id)
        return member

    def get_agent(self, agent_id):
        agent = self.agent_dao.find(agent_id)
        if not agent:
            raise errors.param_not_found('agent_id', 'Agent')
        return agent

    def find_member_agent(self, queue, agent):
        for member in queue.agent_queue_members:
            if member.agent == agent:
                return member
        return None

    def find_member_user(self, queue, user):
        for member in queue.user_queue_members:
            if member.user == user:
                return member
        return None

    def associate_legacy(self, queue, member):
        if member in queue.agent_queue_members:
            raise errors.resource_associated('Agent', 'Queue', member.agent.id, queue.id)
        self.queue_dao.associate_member_agent(queue, member)
        self.notifier.agent_associated(queue, member)

    def associate_member_agent(self, queue, member):
        if member in queue.agent_queue_members:
            return

        self.queue_dao.associate_member_agent(queue, member)
        self.notifier.agent_associated(queue, member)

    def dissociate_member_agent(self, queue, member):
        if member not in queue.agent_queue_members:
            return

        self.queue_dao.dissociate_member_agent(queue, member)
        self.notifier.agent_dissociated(queue, member)

    def associate_member_user(self, queue, member):
        if member in queue.user_queue_members:
            return

        self.validator_member_user.validate_association(queue, member)
        self.queue_dao.associate_member_user(queue, member)
        self.notifier.user_associated(queue, member)

    def dissociate_member_user(self, queue, member):
        if member not in queue.user_queue_members:
            return

        self.queue_dao.dissociate_member_user(queue, member)
        self.notifier.user_dissociated(queue, member)


def build_service():
    return QueueMemberService(
        queue_dao_module,
        agent_dao_module,
        build_validator_member_user(),
        build_notifier(),
    )
