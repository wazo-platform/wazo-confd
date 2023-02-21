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

    def parse_and_update(self, model, body, **kwargs):
        form = self._schema.load(body, partial=True)
        updated_fields = self.find_updated_fields(model, form)
        for name, value in form.items():
            setattr(model, name, value)
        self._service.edit(model, updated_fields=updated_fields, **kwargs)

    def find_updated_fields(self, model, form):
        updated_fields = []
        for name, value in form.items():
            try:
                if getattr(model, name) != value:
                    updated_fields.append(name)
            except AttributeError:
                pass

    def update(self, extension_id, body, tenant_uuids):
        model = self._service.get(extension_id, tenant_uuids=tenant_uuids)
        self.parse_and_update(model, body, tenant_uuids=tenant_uuids)
