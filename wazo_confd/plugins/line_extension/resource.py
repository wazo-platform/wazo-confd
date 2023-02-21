# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for
from xivo.tenant_flask_helpers import Tenant
from xivo_dao import tenant_dao

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource, ListResource


class LineExtensionItem(ConfdResource):
    has_tenant_uuid = True

    def __init__(self, middleware):
        super().__init__()
        self._middleware = middleware

    @required_acl('confd.lines.{line_id}.extensions.{extension_id}.delete')
    def delete(self, line_id, extension_id):
        tenant = Tenant.autodetect()
        tenant_dao.find_or_create_tenant(tenant.uuid)
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.dissociate(line_id, extension_id, tenant.uuid, tenant_uuids)
        return '', 204

    @required_acl('confd.lines.{line_id}.extensions.{extension_id}.update')
    def put(self, line_id, extension_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.associate(line_id, extension_id, tenant_uuids)
        return '', 204


class LineExtensionList(ListResource):
    def __init__(self, middleware):
        self._middleware = middleware

    def build_headers(self, extension):
        return {'Location': url_for('extensions', id=extension['id'], _external=True)}

    @required_acl('confd.lines.{line_id}.extensions.create')
    def post(self, line_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        extension = self._middleware.create_extension(
            line_id,
            request.get_json(),
            tenant_uuids,
        )
        return extension, 201, self.build_headers(extension)

    def _has_a_tenant_uuid(self):
        # The base function does not work because the tenant_uuid is not part
        # of the Extension model and is added by the dao.
        return True
