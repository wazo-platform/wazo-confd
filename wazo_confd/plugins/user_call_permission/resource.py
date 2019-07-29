# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink
from wazo_confd.helpers.restful import ConfdResource


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


class UserCallPermissionAssociation(UserCallPermission):

    has_tenant_uuid = True

    @required_acl('confd.users.{user_id}.callpermissions.{call_permission_id}.update')
    def put(self, user_id, call_permission_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user = self.user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)
        call_permission = self.call_permission_dao.get(call_permission_id, tenant_uuids=tenant_uuids)
        self.service.associate(user, call_permission)
        return '', 204

    @required_acl('confd.users.{user_id}.callpermissions.{call_permission_id}.delete')
    def delete(self, user_id, call_permission_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user = self.user_dao.get_by_id_uuid(user_id, tenant_uuids=tenant_uuids)
        call_permission = self.call_permission_dao.get(call_permission_id, tenant_uuids=tenant_uuids)
        self.service.dissociate(user, call_permission)
        return '', 204


class UserCallPermissionGet(UserCallPermission):

    schema = UserCallPermissionSchema

    @required_acl('confd.users.{user_id}.callpermissions.read')
    def get(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        user_call_permissions = self.service.find_all_by(user_id=user.id)
        return {'total': len(user_call_permissions),
                'items': self.schema().dump(user_call_permissions, many=True)}


class CallPermissionUserGet(UserCallPermission):

    schema = UserCallPermissionSchema

    @required_acl('confd.callpermissions.{call_permission_id}.users.read')
    def get(self, call_permission_id):
        call_permission = self.call_permission_dao.get(call_permission_id)
        user_call_permissions = self.service.find_all_by(call_permission_id=call_permission.id)
        return {'total': len(user_call_permissions),
                'items': self.schema().dump(user_call_permissions, many=True)}
