# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for
from uuid import uuid4

from xivo_dao.alchemy.rightcall import RightCall as CallPermission

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import CallPermissionSchema


class CallPermissionList(ListResource):
    model = CallPermission
    schema = CallPermissionSchema
    call_permission_name_fmt = 'cpm-{tenant_slug}-{call_permission_uuid}'

    def __init__(self, tenant_dao, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant_dao = tenant_dao

    def build_headers(self, call_permission):
        return {
            'Location': url_for(
                'callpermissions', id=call_permission.id, _external=True
            )
        }

    @required_acl('confd.callpermissions.create')
    def post(self):
        form = self.schema().load(request.get_json())
        form = self.add_tenant_to_form(form)

        tenant = self._tenant_dao.get(form['tenant_uuid'])
        # NOTE(afournier): we use a UUID as if it was the call permission UUID but it's not
        # Call permissions do not use UUIDs yet
        form['name'] = self.call_permission_name_fmt.format(
            tenant_slug=tenant.slug,
            call_permission_uuid=uuid4(),
        )
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

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
