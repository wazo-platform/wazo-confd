# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import ExtensionSchema


class ExtensionList(ListResource):
    schema = ExtensionSchema

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    def build_headers(self, extension):
        return {'Location': url_for('extensions', id=extension['id'], _external=True)}

    @required_acl('confd.extensions.read')
    def get(self):
        return super().get()

    @required_acl('confd.extensions.create')
    def post(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        resource = self._middleware.create(
            request.get_json(),
            tenant_uuids,
        )
        return resource, 201, self.build_headers(resource)

    def _has_a_tenant_uuid(self):
        # The base function does not work because the tenant_uuid is not part
        # of the Extension model and is added by the dao.
        return True


class ExtensionItem(ItemResource):
    schema = ExtensionSchema
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    @required_acl('confd.extensions.{id}.read')
    def get(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        return self._middleware.get(id, tenant_uuids)

    @required_acl('confd.extensions.{id}.update')
    def put(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.update(id, request.get_json(), tenant_uuids)
        return '', 204

    @required_acl('confd.extensions.{id}.delete')
    def delete(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.delete(id, tenant_uuids)
        return '', 204
