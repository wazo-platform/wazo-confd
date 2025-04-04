# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPEndpoint

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource, build_tenant

from .schema import SccpSchema


class SccpList(ListResource):
    model = SCCPEndpoint
    schema = SccpSchema

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    def build_headers(self, sccp):
        return {'Location': url_for('endpoint_sccp', id=sccp['id'], _external=True)}

    @required_acl('confd.endpoints.sccp.read')
    def get(self):
        return super().get()

    @required_acl('confd.endpoints.sccp.create')
    def post(self):
        tenant_uuid = build_tenant()
        resource = self._middleware.create(request.get_json(), tenant_uuid)
        return resource, 201, self.build_headers(resource)


class SccpItem(ItemResource):
    schema = SccpSchema
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    @required_acl('confd.endpoints.sccp.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.endpoints.sccp.{id}.update')
    def put(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.update(id, request.get_json(), tenant_uuids)
        return '', 204

    @required_acl('confd.endpoints.sccp.{id}.delete')
    def delete(self, id):
        return super().delete(id)
