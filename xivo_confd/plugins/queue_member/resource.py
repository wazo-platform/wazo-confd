# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request, url_for
from marshmallow import fields
from marshmallow.validate import Range

from xivo_dao.resources.queue_members.model import QueueMemberAgent

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource
from xivo_confd.helpers.mallow import BaseSchema


class QueueMemberSchema(BaseSchema):
    agent_id = fields.Integer()
    queue_id = fields.Integer()
    penalty = fields.Integer(validate=Range(min=0), missing=0)


class QueueMemberResource(ConfdResource):

    def __init__(self, service):
        super(QueueMemberResource, self).__init__()
        self.service = service


class QueueMemberAssociation(QueueMemberResource):

    schema = QueueMemberSchema

    @required_acl('confd.queues.{queue_id}.members.{agent_id}.read')
    def get(self, queue_id, agent_id):
        queue_member_agent = self.service.get(queue_id, agent_id)
        return self.schema().dump(queue_member_agent).data

    @required_acl('confd.queues.{queue_id}.members.{agent_id}.update')
    def put(self, queue_id, agent_id):
        form = self.schema().load(request.get_json(), partial=True).data
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

    schema = QueueMemberSchema
    model = QueueMemberAgent

    def build_headers(self, queue_member):
        return {'Location': url_for('queuemembers',
                                    queue_id=queue_member.queue_id,
                                    agent_id=queue_member.agent_id,
                                    _external=True)}

    @required_acl('confd.queues.{queue_id}.members.create')
    def post(self, queue_id):
        form = self.schema().load(request.get_json()).data
        form['queue_id'] = queue_id
        model = self.model(**form)
        model = self.service.associate(model)
        return self.schema().dump(model).data, 201, self.build_headers(model)
