# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for

from xivo_dao.alchemy.extension import Extension

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource, ListResource
from wazo_confd.plugins.extension.schema import ExtensionSchema


class LineExtensionItem(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, line_dao, extension_dao):
        super().__init__()
        self.service = service
        self.line_dao = line_dao
        self.extension_dao = extension_dao

    @required_acl('confd.lines.{line_id}.extensions.{extension_id}.delete')
    def delete(self, line_id, extension_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)
        extension = self.extension_dao.get(extension_id, tenant_uuids=tenant_uuids)

        self.service.dissociate(line, extension)
        return '', 204

    @required_acl('confd.lines.{line_id}.extensions.{extension_id}.update')
    def put(self, line_id, extension_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)
        extension = self.extension_dao.get(extension_id, tenant_uuids=tenant_uuids)

        self.service.associate(line, extension)
        return '', 204


class LineExtensionList(ListResource):

    model = Extension
    schema = ExtensionSchema

    def __init__(self, extension_line_service, extension_service, line_dao):
        self.service = extension_line_service
        self.extension_service = extension_service
        self.line_dao = line_dao

    def build_headers(self, extension):
        return {'Location': url_for('extensions', id=extension.id, _external=True)}

    @required_acl('confd.lines.{line_id}.extensions.create')
    def post(self, line_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)

        form = self.schema().load(request.get_json())
        model = self.model(**form)
        extension = self.extension_service.create(model, tenant_uuids)

        self.service.associate(line, extension)

        return self.schema().dump(extension), 201, self.build_headers(extension)

    def _has_a_tenant_uuid(self):
        # The base function does not work because the tenant_uuid is not part
        # of the Extension model and is added by the dao.
        return True
