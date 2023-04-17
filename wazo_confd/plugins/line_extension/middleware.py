# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from xivo_dao.helpers.exception import ResourceError
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.extension import dao as extension_dao


class LineExtensionMiddleware:
    def __init__(self, service, middleware_handle):
        self._service = service
        self._middleware_handle = middleware_handle

    def associate(self, line_id, extension_id, tenant_uuids):
        line = line_dao.get(line_id, tenant_uuids=tenant_uuids)
        extension = extension_dao.get(extension_id, tenant_uuids=tenant_uuids)
        self._service.associate(line, extension)

    def dissociate(
        self, line_id, extension_id, tenant_uuid, tenant_uuids, reset_autoprov=False
    ):
        line = line_dao.get(line_id, tenant_uuids=tenant_uuids)
        if line.device_id and reset_autoprov:
            self._middleware_handle.get('device').reset_autoprov(
                line.device_id, tenant_uuid
            )
        extension = extension_dao.get(extension_id, tenant_uuids=tenant_uuids)
        self._service.dissociate(line, extension)

    def create_extension(self, line_id, body, tenant_uuids):
        extension_middleware = self._middleware_handle.get('extension')
        extension = extension_middleware.create(body, tenant_uuids)
        self.associate(line_id, extension['id'], tenant_uuids)
        return extension

    def delete_extension(self, line_id, extension_id, tenant_uuid, tenant_uuids):
        extension_middleware = self._middleware_handle.get('extension')
        self.dissociate(
            line_id, extension_id, tenant_uuid, tenant_uuids, reset_autoprov=True
        )
        try:
            extension_middleware.delete(extension_id, tenant_uuids)
        except ResourceError as e:
            if not str(e).startswith('Resource Error - Extension is associated'):
                raise e
