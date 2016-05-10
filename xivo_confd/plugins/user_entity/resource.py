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

from flask_restful import fields, marshal

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import FieldList, Link, ConfdResource


fields = {
    'user_id': fields.Integer,
    'entity_id': fields.Integer,
    'links': FieldList(Link('users',
                            field='user_id',
                            target='id'))
}


class UserEntityResource(ConfdResource):

    def __init__(self, service, user_dao, entity_dao):
        super(UserEntityResource, self).__init__()
        self.service = service
        self.user_dao = user_dao
        self.entity_dao = entity_dao

    def get_user(self, user_id):
        return self.user_dao.get_by_id_uuid(user_id)


class UserEntityItem(UserEntityResource):

    @required_acl('confd.users.{user_id}.entities.{entity_id}.update')
    def put(self, user_id, entity_id):
        user = self.get_user(user_id)
        self.service.associate(user, entity_id)
        return '', 204


class UserEntityList(UserEntityResource):

    @required_acl('confd.users.{user_id}.entities.read')
    def get(self, user_id):
        user = self.get_user(user_id)
        item = self.service.find_by_user_id(user.id)
        return marshal(item, fields)
