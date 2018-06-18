# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ConfdResource


class UserAgentSchema(BaseSchema):
    user_id = fields.Integer(attribute='id')
    agent_id = fields.Integer()
    links = ListLink(Link('users',
                          field='id',
                          target='id'))


class UserAgentItem(ConfdResource):

    def __init__(self, service, user_dao, agent_dao):
        super(UserAgentItem, self).__init__()
        self.service = service
        self.user_dao = user_dao
        self.agent_dao = agent_dao

    @required_acl('confd.users.{user_id}.agents.{agent_id}.update')
    def put(self, user_id, agent_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        agent = self.agent_dao.get(agent_id)
        self.service.associate(user, agent)
        return '', 204


class UserAgentList(ConfdResource):

    schema = UserAgentSchema

    def __init__(self, service, user_dao):
        super(UserAgentList, self).__init__()
        self.service = service
        self.user_dao = user_dao

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
