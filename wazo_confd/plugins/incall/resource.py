# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo.tenant_flask_helpers import Tenant
from xivo_dao.alchemy.incall import Incall
from xivo_dao import tenant_dao

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import IncallSchema


class IncallList(ListResource):
    model = Incall
    schema = IncallSchema

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    def build_headers(self, incall):
        return {'Location': url_for('incalls', id=incall['id'], _external=True)}

    @required_acl('confd.incalls.create')
    def post(self):
        tenant = Tenant.autodetect()
        tenant_dao.find_or_create_tenant(tenant.uuid)
        resource = self._middleware.create(request.get_json(), tenant.uuid)
        return resource, 201, self.build_headers(resource)

    @required_acl('confd.incalls.read')
    def get(self):
        return super().get()


class IncallItem(ItemResource):
    schema = IncallSchema
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    @required_acl('confd.incalls.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.incalls.{id}.update')
    def put(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.update(id, request.get_json(), tenant_uuids)
        return '', 204

    @required_acl('confd.incalls.{id}.delete')
    def delete(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.delete(id, tenant_uuids)
        return '', 204
