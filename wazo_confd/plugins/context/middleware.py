# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .schema import ContextSchemaPUT


class ContextMiddleWare:
    def __init__(self, service):
        self._schema = ContextSchemaPUT()
        self._schema_update = ContextSchemaPUT()
        self._service = service

    def get(self, context_id, tenant_uuids):
        model = self._service.get(context_id, tenant_uuids=tenant_uuids)
        return self._schema.dump(model)

    def get_by_name(self, context_name, tenant_uuids):
        model = self._service.get_by(name=context_name, tenant_uuids=tenant_uuids)
        return self._schema.dump(model)

    def parse_and_update(self, model, body, **kwargs):
        form = self._schema_update.load(body, partial=True)
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
        return updated_fields

    def update(self, context_id, body, tenant_uuids):
        model = self._service.get(context_id, tenant_uuids=tenant_uuids)
        self.parse_and_update(model, body)
