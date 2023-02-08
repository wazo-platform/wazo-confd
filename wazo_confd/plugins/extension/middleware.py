# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.extension import Extension

from .schema import ExtensionSchema


class ExtensionMiddleWare:
    def __init__(self, service):
        self._schema = ExtensionSchema()
        self._service = service

    def create(self, body, tenant_uuids):
        form = self._schema.load(body)
        model = Extension(**form)
        model = self._service.create(model, tenant_uuids)
        return self._schema.dump(model)

    def delete(self, extension_id, tenant_uuids):
        model = self._service.get(extension_id, tenant_uuids=tenant_uuids)
        self._service.delete(model)

    def get(self, extension_id, tenant_uuids):
        model = self._service.get(extension_id, tenant_uuids=tenant_uuids)
        return self._schema.dump(model)

    def get_by(self, tenant_uuids, **criteria):
        model = self._service.get_by(tenant_uuids=tenant_uuids, **criteria)
        return self._schema.dump(model)
