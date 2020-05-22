# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.rightcall import RightCall as CallPermission

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import CallPermissionSchema


class CallPermissionList(ListResource):

    model = CallPermission
    schema = CallPermissionSchema

    def build_headers(self, call_permission):
        return {
            'Location': url_for(
                'callpermissions', id=call_permission.id, _external=True
            )
        }

    @required_acl('confd.callpermissions.create')
    def post(self):
        return super().post()

    @required_acl('confd.callpermissions.read')
    def get(self):
        return super().get()


class CallPermissionItem(ItemResource):

    schema = CallPermissionSchema
    has_tenant_uuid = True

    @required_acl('confd.callpermissions.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.callpermissions.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.callpermissions.{id}.delete')
    def delete(self, id):
        return super().delete(id)
