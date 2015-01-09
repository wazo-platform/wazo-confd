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

from flask import Blueprint
from flask import request, make_response, url_for
from flask_negotiate import produces
from flask_negotiate import consumes

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int
from xivo_dao.data_handler.queue_members import services
from xivo_dao.data_handler.queue_members.model import QueueMemberAgent


def load(core_rest_api):
    blueprint = Blueprint('queues', __name__, url_prefix='/%s/queues' % config.API_VERSION)
    document = core_rest_api.content_parser.document(
        Field('queue_id', Int()),
        Field('agent_id', Int()),
        Field('penalty', Int())
    )
    converter = Converter.for_request(document, QueueMemberAgent)

    @blueprint.route('/<int:queue_id>/members/agents/<int:agent_id>')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get_agent_queue_association(queue_id, agent_id):
        queue_member = services.get_by_queue_id_and_agent_id(queue_id, agent_id)
        return make_response(converter.encode(queue_member), 200)

    @blueprint.route('/<int:queue_id>/members/agents/<int:agent_id>', methods=['PUT'])
    @core_rest_api.auth.login_required
    @consumes('application/json')
    def edit_agent_queue_association(queue_id, agent_id):
        queue_member = converter.decode(request)
        services.edit_agent_queue_association(queue_member)
        return make_response('', 204)

    @blueprint.route('/<int:queue_id>/members/agents', methods=['POST'])
    @core_rest_api.auth.login_required
    @produces('application/json')
    @consumes('application/json')
    def associate_agent_to_queue(queue_id):
        queue_member = converter.decode(request)
        created_queue_member = services.associate_agent_to_queue(queue_member)
        location = url_for('.get_agent_queue_association',
                           queue_id=created_queue_member.queue_id,
                           agent_id=created_queue_member.agent_id)
        return make_response(converter.encode(created_queue_member), 201, {'Location': location})

    @blueprint.route('/<int:queue_id>/members/agents/<int:agent_id>', methods=['DELETE'])
    @core_rest_api.auth.login_required
    def remove_agent_from_queue(agent_id, queue_id):
        services.remove_agent_from_queue(agent_id, queue_id)
        return make_response('', 204)

    core_rest_api.register(blueprint)
