# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import fields
from marshmallow.validate import Range
from xivo_dao.alchemy.queuemember import QueueMember

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema
from wazo_confd.helpers.restful import ConfdResource


class QueueMemberAgentSchema(BaseSchema):
    penalty = fields.Integer(validate=Range(min=0), load_default=0)
    priority = fields.Integer(validate=Range(min=0), load_default=0)


class QueueMemberUserSchema(BaseSchema):
    priority = fields.Integer(validate=Range(min=0), load_default=0)


class QueueMemberAgentItem(ConfdResource):
    schema = QueueMemberAgentSchema
    has_tenant_uuid = True

    def __init__(self, middleware):
        super().__init__()
        self._middleware = middleware

    @required_acl('confd.queues.{queue_id}.members.agents.{agent_id}.update')
    def put(self, queue_id, agent_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.associate(
            request.get_json(force=True), queue_id, agent_id, tenant_uuids
        )
        return '', 204

    @required_acl('confd.queues.{queue_id}.members.agents.{agent_id}.delete')
    def delete(self, queue_id, agent_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.dissociate(queue_id, agent_id, tenant_uuids)
        return '', 204


class QueueMemberUserItem(ConfdResource):
    schema = QueueMemberUserSchema
    has_tenant_uuid = True

    def __init__(self, service, queue_dao, user_dao):
        super().__init__()
        self.service = service
        self.queue_dao = queue_dao
        self.user_dao = user_dao

    @required_acl('confd.queues.{queue_id}.members.users.{user_id}.update')
    def put(self, queue_id, user_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        queue = self.queue_dao.get(queue_id, tenant_uuids=tenant_uuids)
        user = self.user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)
        member = self._find_or_create_member(queue, user)
        form = self.schema().load(request.get_json(force=True))
        setattr(member, 'priority', form['priority'])
        self.service.associate_member_user(queue, member)
        return '', 204

    @required_acl('confd.queues.{queue_id}.members.users.{user_id}.delete')
    def delete(self, queue_id, user_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        queue = self.queue_dao.get(queue_id, tenant_uuids=tenant_uuids)
        user = self.user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)
        member = self._find_or_create_member(queue, user)
        self.service.dissociate_member_user(queue, member)
        return '', 204

    def _find_or_create_member(self, queue, user):
        member = self.service.find_member_user(queue, user)
        if not member:
            member = QueueMember(user=user)
        return member
