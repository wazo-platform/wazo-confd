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

from flask import request, make_response

from xivo_dao.data_handler.queue_members import services
from xivo_dao.data_handler.queue_members.model import QueueMemberAgent
from xivo_restapi.flask_http_server import content_parser
from xivo_restapi.helpers import serializer
from xivo_restapi.helpers.formatter import Formatter
from xivo_restapi.helpers.premacop import Field, Int
from xivo_restapi.resources.queue_members import mapper
from xivo_restapi.resources.queues.routes import queue_route


formatter = Formatter(mapper, serializer, QueueMemberAgent)
document = content_parser.document(
    Field('penalty', Int())
)


@queue_route('/<int:queueid>/memberships/agents/<int:agentid>')
def get_agent_queue_association(queueid, agentid):
    result = services.get_by_queue_id_and_agent_id(queueid, agentid)
    return make_response(formatter.to_api(result), 200)


@queue_route('/<int:queueid>/memberships/agents/<int:agentid>', methods=['PUT'])
def edit_agent_queue_association(queueid, agentid):
    data = document.parse(request)
    data['agent_id'] = agentid
    data['queue_id'] = queueid
    model = formatter.dict_to_model(data)
    services.edit_agent_queue_association(model)
    return make_response('', 204)
