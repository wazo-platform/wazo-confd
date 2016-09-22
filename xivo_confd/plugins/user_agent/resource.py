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
