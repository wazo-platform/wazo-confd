# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import request, make_response, url_for

from xivo_dao.data_handler.queue_members import services
from xivo_confd.resources.queues.routes import queue_route
from xivo_confd.resources.queue_members.converter import converter


@queue_route('/<int:queue_id>/members/agents/<int:agent_id>')
def get_agent_queue_association(queue_id, agent_id):
    queue_member = services.get_by_queue_id_and_agent_id(queue_id, agent_id)
    return make_response(converter.encode(queue_member), 200)


@queue_route('/<int:queue_id>/members/agents/<int:agent_id>', methods=['PUT'])
def edit_agent_queue_association(queue_id, agent_id):
    queue_member = converter.decode(request)
    services.edit_agent_queue_association(queue_member)
    return make_response('', 204)


@queue_route('/<int:queue_id>/members/agents', methods=['POST'])
def associate_agent_to_queue(queue_id):
    queue_member = converter.decode(request)
    created_queue_member = services.associate_agent_to_queue(queue_member)
    location = url_for('.get_agent_queue_association',
                       queue_id=created_queue_member.queue_id,
                       agent_id=created_queue_member.agent_id)
    return make_response(converter.encode(created_queue_member), 201, {'Location': location})


@queue_route('/<int:queue_id>/members/agents/<int:agent_id>', methods=['DELETE'])
def remove_agent_from_queue(agent_id, queue_id):
    services.remove_agent_from_queue(agent_id, queue_id)
    return make_response('', 204)
