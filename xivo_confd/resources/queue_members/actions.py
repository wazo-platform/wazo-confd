# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2015 Avencall
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
from flask import request
from flask import url_for

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int
from xivo_confd.helpers.resource import CollectionAssociationResource, DecoratorChain, build_response

from xivo_dao.data_handler.queue_members import dao
from xivo_dao.data_handler.queue_members import validator
from xivo_dao.data_handler.queue_members import notifier
from xivo_dao.resources.queue_members.model import QueueMemberAgent


class QueueMemberService(object):

    def __init__(self, dao, validator, notifier):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier

    def get(self, queue_id, agent_id):
        self.validator.validate_get_agent_queue_association(queue_id, agent_id)
        return self.dao.get_by_queue_id_and_agent_id(queue_id, agent_id)

    def edit(self, queue_member):
        self.validator.validate_edit_agent_queue_association(queue_member)
        self.dao.edit_agent_queue_association(queue_member)
        self.notifier.agent_queue_association_updated(queue_member)

    def associate(self, queue_member):
        self.validator.validate_associate_agent_queue(queue_member.queue_id, queue_member.agent_id)
        qm = self.dao.associate(queue_member)
        self.notifier.agent_queue_associated(queue_member)
        return qm

    def dissociate(self, queue_member):
        self.validator.validate_remove_agent_from_queue(queue_member.agent_id, queue_member.queue_id)
        self.dao.remove_agent_from_queue(queue_member.agent_id, queue_member.queue_id)
        self.notifier.agent_removed_from_queue(queue_member.agent_id, queue_member.queue_id)


class QueueMemberAssociationResource(CollectionAssociationResource):

    def get_association(self, parent_id, resource_id):
        association = self.service.get(parent_id, resource_id)
        response = self.converter.encode(association)
        location = url_for('.get_association',
                           parent_id=parent_id,
                           resource_id=resource_id)
        return build_response(response, location=location)

    def edit_association(self, parent_id, resource_id):
        association = self.converter.decode(request)
        self.service.edit(association)
        return ('', 204)

    def associate_collection(self, parent_id):
        association = self.converter.decode(request)
        created_association = self.service.associate(association)
        response = self.converter.encode(created_association)
        location = url_for('.get_association',
                           parent_id=parent_id,
                           resource_id=created_association.agent_id)
        return build_response(response, 201, location)

    def dissociate_collection(self, parent_id, resource_id):
        association = self.service.get(parent_id, resource_id)
        self.service.dissociate(association)
        return ('', 204)


def load(core_rest_api):
    blueprint = Blueprint('queues', __name__, url_prefix='/%s/queues' % config.API_VERSION)
    document = core_rest_api.content_parser.document(
        Field('queue_id', Int()),
        Field('agent_id', Int()),
        Field('penalty', Int())
    )
    converter = Converter.association(document, QueueMemberAgent,
                                      rename={'parent_id': 'queue_id',
                                              'resource_id': 'agent_id'})

    service = QueueMemberService(dao, validator, notifier)
    resource = QueueMemberAssociationResource(service, converter)

    chain = DecoratorChain(core_rest_api, blueprint)

    (chain
     .get('/<int:parent_id>/members/agents/<int:resource_id>')
     .decorate(resource.get_association))

    (chain
     .edit('/<int:parent_id>/members/agents/<int:resource_id>')
     .decorate(resource.edit_association))

    (chain
     .create('/<int:parent_id>/members/agents')
     .decorate(resource.associate_collection))

    (chain
     .delete('/<int:parent_id>/members/agents/<int:resource_id>')
     .decorate(resource.dissociate_collection))

    core_rest_api.register(blueprint)
