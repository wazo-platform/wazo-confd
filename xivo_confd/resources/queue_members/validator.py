# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_dao import queue_dao, agent_dao
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers import errors
from xivo_dao.resources.queue_members import dao as queue_members_dao


def validate_edit_agent_queue_association(queue_member):
    if not _queue_exists(queue_member.queue_id):
        raise errors.not_found('Queue', queue_id=queue_member.queue_id)
    if not _agent_exists(queue_member.agent_id):
        raise errors.not_found('Agent', agent_id=queue_member.agent_id)
    queue_members_dao.get_by_queue_id_and_agent_id(queue_member.queue_id, queue_member.agent_id)


def validate_get_agent_queue_association(queue_id, agent_id):
    if not _queue_exists(queue_id):
        raise errors.not_found('Queue', queue_id=queue_id)
    if not _agent_exists(agent_id):
        raise errors.not_found('Agent', agent_id=agent_id)


def validate_associate_agent_queue(queue_id, agent_id):
    if not _queue_exists(queue_id):
        raise errors.not_found('Queue', queue_id=queue_id)
    if not _agent_exists(agent_id):
        raise errors.param_not_found('agent_id', 'Agent')
    try:
        queue_members_dao.get_by_queue_id_and_agent_id(queue_id, agent_id)
        raise errors.resource_associated('Agent', 'Queue',
                                         agent_id, queue_id)
    except NotFoundError:
        pass


def validate_remove_agent_from_queue(agent_id, queue_id):
    if not _queue_exists(queue_id):
        raise errors.not_found('Queue', queue_id=queue_id)
    if not _agent_exists(agent_id):
        raise errors.not_found('Agent', agent_id=agent_id)
    queue_members_dao.get_by_queue_id_and_agent_id(queue_id, agent_id)


def _queue_exists(queue_id):
    try:
        return queue_dao.get(queue_id) is not None
    except LookupError:
        return False


def _agent_exists(agent_id):
    return agent_dao.get(agent_id) is not None
