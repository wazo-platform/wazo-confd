# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


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
