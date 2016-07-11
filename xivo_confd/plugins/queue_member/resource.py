# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from flask import request, url_for
from marshmallow import fields
from marshmallow.validate import Range

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource
from xivo_confd.helpers.mallow import BaseSchema
from xivo_dao.resources.queue_members.model import QueueMemberAgent


class QueueMemberSchema(BaseSchema):
    agent_id = fields.Integer()
    queue_id = fields.Integer()
    penalty = fields.Integer(validate=Range(min=0), missing=0)


class QueueMemberResource(ConfdResource):

    def __init__(self, service):
        super(QueueMemberResource, self).__init__()
        self.service = service


class QueueMemberAssociation(QueueMemberResource):

    schema = QueueMemberSchema()

    @required_acl('confd.queues.{queue_id}.members.{agent_id}.read')
    def get(self, queue_id, agent_id):
        queue_member_agent = self.service.get(queue_id, agent_id)
        return self.schema.dump(queue_member_agent).data

    @required_acl('confd.queues.{queue_id}.members.{agent_id}.update')
    def put(self, queue_id, agent_id):
        form = self.schema.load(request.get_json(), partial=True).data
        model = self.service.get(queue_id, agent_id)
        setattr(model, 'penalty', form['penalty'])
        self.service.edit(model)
        return '', 204

    @required_acl('confd.queues.{queue_id}.members.{agent_id}.delete')
    def delete(self, queue_id, agent_id):
        queue_member_agent = self.service.get(queue_id, agent_id)
        self.service.dissociate(queue_member_agent)
        return '', 204


class QueueMemberPost(QueueMemberResource):

    schema = QueueMemberSchema()
    model = QueueMemberAgent

    def build_headers(self, queue_member):
        return {'Location': url_for('queuemembers',
                                    queue_id=queue_member.queue_id,
                                    agent_id=queue_member.agent_id,
                                    _external=True)}

    @required_acl('confd.queues.{queue_id}.members.create')
    def post(self, queue_id):
        form = self.schema.load(request.get_json()).data
        form['queue_id'] = queue_id
        model = self.model(**form)
        model = self.service.associate(model)
        return self.schema.dump(model).data, 201, self.build_headers(model)
