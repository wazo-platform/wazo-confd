# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao import queue_dao, agent_dao
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers import errors
from xivo_dao.resources.queue_members import dao as queue_members_dao


class QueueMemberAssociationValidator(object):

    def validate_edit_agent_queue_association(self, queue_member):
        if not self._queue_exists(queue_member.queue_id):
            raise errors.not_found('Queue', queue_id=queue_member.queue_id)
        if not self._agent_exists(queue_member.agent_id):
            raise errors.not_found('Agent', agent_id=queue_member.agent_id)
        queue_members_dao.get_by_queue_id_and_agent_id(queue_member.queue_id, queue_member.agent_id)

    def validate_get_agent_queue_association(self, queue_id, agent_id):
        if not self._queue_exists(queue_id):
            raise errors.not_found('Queue', queue_id=queue_id)
        if not self._agent_exists(agent_id):
            raise errors.not_found('Agent', agent_id=agent_id)

    def validate_associate_agent_queue(self, queue_id, agent_id):
        if not self._queue_exists(queue_id):
            raise errors.not_found('Queue', queue_id=queue_id)
        if not self._agent_exists(agent_id):
            raise errors.param_not_found('agent_id', 'Agent')
        try:
            queue_members_dao.get_by_queue_id_and_agent_id(queue_id, agent_id)
            raise errors.resource_associated('Agent', 'Queue',
                                             agent_id, queue_id)
        except NotFoundError:
            pass

    def validate_remove_agent_from_queue(self, queue_id, agent_id):
        if not self._queue_exists(queue_id):
            raise errors.not_found('Queue', queue_id=queue_id)
        if not self._agent_exists(agent_id):
            raise errors.not_found('Agent', agent_id=agent_id)
        queue_members_dao.get_by_queue_id_and_agent_id(queue_id, agent_id)

    def _queue_exists(self, queue_id):
        try:
            return queue_dao.get(queue_id) is not None
        except LookupError:
            return False

    def _agent_exists(self, agent_id):
        return agent_dao.get(agent_id) is not None


def build_validator():
    return QueueMemberAssociationValidator()
