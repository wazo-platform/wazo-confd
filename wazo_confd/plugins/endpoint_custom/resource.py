# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo.tenant_flask_helpers import Tenant

from xivo_dao import tenant_dao
from xivo_dao.alchemy.usercustom import UserCustom as Custom

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import CustomSchema


class CustomList(ListResource):

    model = Custom
    schema = CustomSchema

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    def build_headers(self, custom):
        return {'Location': url_for('endpoint_custom', id=custom['id'], _external=True)}

    @required_acl('confd.endpoints.custom.read')
    def get(self):
        return super().get()

    @required_acl('confd.endpoints.custom.create')
    def post(self):
        tenant = Tenant.autodetect()
        tenant_dao.find_or_create_tenant(tenant.uuid)
        resource = self._middleware.create(request.get_json(), tenant.uuid)
        return resource, 201, self.build_headers(resource)


class CustomItem(ItemResource):

    schema = CustomSchema
    has_tenant_uuid = True

    @required_acl('confd.endpoints.custom.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.endpoints.custom.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.endpoints.custom.{id}.delete')
    def delete(self, id):
        return super().delete(id)
