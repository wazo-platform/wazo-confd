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
from xivo_dao.data_handler.queue_members.model import QueueMemberAgent
from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers import serializer
from xivo_confd.helpers.formatter import Formatter
from xivo_confd.helpers.mooltiparse import Field, Int
from xivo_confd.resources.queue_members import mapper
from xivo_confd.resources.queues.routes import queue_route


formatter = Formatter(mapper, serializer, QueueMemberAgent)
document = content_parser.document(
    Field('penalty', Int())
)


@queue_route('/<int:queueid>/members/agents/<int:agentid>')
def get_agent_queue_association(queueid, agentid):
    result = services.get_by_queue_id_and_agent_id(queueid, agentid)
    return make_response(formatter.to_api(result), 200)


@queue_route('/<int:queueid>/members/agents/<int:agentid>', methods=['PUT'])
def edit_agent_queue_association(queueid, agentid):
    data = document.parse(request)
    queue_member = QueueMemberAgent()
    queue_member.penalty = data['penalty']
    queue_member.agent_id = agentid
    queue_member.queue_id = queueid
    services.edit_agent_queue_association(queue_member)
    return make_response('', 204)


@queue_route('/<int:queueid>/members/agents', methods=['POST'])
def associate_agent_to_queue(queueid):
    data = document.parse(request)
    queue_member = QueueMemberAgent(agent_id=data['agent_id'], queue_id=queueid, penalty=data['penalty'])
    result = services.associate_agent_to_queue(queue_member)
    location = url_for('.get_agent_queue_association', queueid=queueid, agentid=queue_member.agent_id)
    return make_response(formatter.to_api(result), 201, {'Location': location})


@queue_route('/<int:queueid>/members/agents/<int:agentid>', methods=['DELETE'])
def remove_agent_from_queue(agentid, queueid):
    services.remove_agent_from_queue(agentid, queueid)
    return make_response('', 204)
