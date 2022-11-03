# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.extension import dao as extension_dao


class LineExtensionMiddleware:
    def __init__(self, service, middleware_handle):
        self._service = service
        self._middleware_handle = middleware_handle

    def associate(self, line_id, extension_id, tenant_uuids):
        line = line_dao.get(line_id, tenant_uuids=tenant_uuids)
        extension = extension_dao.get(extension_id, tenant_uuids=tenant_uuids)
        return self._service.associate(line, extension)

    def dissociate(self, line_id, extension_id, tenant_uuids):
        line = line_dao.get(line_id, tenant_uuids=tenant_uuids)
        extension = extension_dao.get(extension_id, tenant_uuids=tenant_uuids)
        return self._service.dissociate(line, extension)

    def create_extension(self, line_id, body, tenant_uuids):
        extension_middleware = self._middleware_handle.get('extension')
        extension = extension_middleware.create(body, tenant_uuids)
        self.associate(line_id, extension['id'], tenant_uuids)
        return extension
