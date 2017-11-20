# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ConfdResource


class UserAgentSchema(BaseSchema):
    user_id = fields.Integer(attribute='id')
    agent_id = fields.Integer()
    links = ListLink(Link('users',
                          field='id',
                          target='id'))


class UserAgentResource(ConfdResource):

    def __init__(self, service, user_dao):
        super(UserAgentResource, self).__init__()
        self.service = service
        self.user_dao = user_dao


class UserAgentItem(UserAgentResource):

    @required_acl('confd.users.{user_id}.agents.{agent_id}.update')
    def put(self, user_id, agent_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        self.service.associate(user, agent_id)
        return '', 204


class UserAgentList(UserAgentResource):

    schema = UserAgentSchema

    @required_acl('confd.users.{user_id}.agents.read')
    def get(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        item = self.service.find_by_user_id(user.id)
        return self.schema().dump(item).data

    @required_acl('confd.users.{user_id}.agents.delete')
    def delete(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        self.service.dissociate(user)
        return '', 204
