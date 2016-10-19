# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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


class UserCallPermissionSchema(BaseSchema):
    user_id = fields.Integer()
    call_permission_id = fields.Integer()
    links = ListLink(Link('users',
                          field='user_id',
                          target='id'),
                     Link('callpermissions',
                          field='call_permission_id',
                          target='id'))


class UserCallPermission(ConfdResource):

    def __init__(self, service, user_dao, call_permission_dao):
        super(UserCallPermission, self).__init__()
        self.service = service
        self.user_dao = user_dao
        self.call_permission_dao = call_permission_dao

    def get_user(self, user_id):
        return self.user_dao.get_by_id_uuid(user_id)


class UserCallPermissionAssociation(UserCallPermission):

    @required_acl('confd.users.{user_id}.callpermissions.{call_permission_id}.update')
    def put(self, user_id, call_permission_id):
        user = self.get_user(user_id)
        call_permission = self.call_permission_dao.get(call_permission_id)
        self.service.associate(user, call_permission)
        return '', 204

    @required_acl('confd.users.{user_id}.callpermissions.{call_permission_id}.delete')
    def delete(self, user_id, call_permission_id):
        user = self.get_user(user_id)
        call_permission = self.call_permission_dao.get(call_permission_id)
        self.service.dissociate(user, call_permission)
        return '', 204


class UserCallPermissionGet(UserCallPermission):

    schema = UserCallPermissionSchema

    @required_acl('confd.users.{user_id}.callpermissions.read')
    def get(self, user_id):
        user = self.get_user(user_id)
        user_call_permissions = self.service.find_all_by(user_id=user.id)
        return {'total': len(user_call_permissions),
                'items': self.schema().dump(user_call_permissions, many=True).data}


class CallPermissionUserGet(UserCallPermission):

    schema = UserCallPermissionSchema

    @required_acl('confd.callpermissions.{call_permission_id}.users.read')
    def get(self, call_permission_id):
        call_permission = self.call_permission_dao.get(call_permission_id)
        user_call_permissions = self.service.find_all_by(call_permission_id=call_permission.id)
        return {'total': len(user_call_permissions),
                'items': self.schema().dump(user_call_permissions, many=True).data}
