# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .schema import ContextSchemaPUT


class ContextMiddleWare:
    def __init__(self, service):
        self._schema = ContextSchemaPUT()
        self._schema_update = ContextSchemaPUT()
        self._service = service

    def get(self, **criteria):
        model = self._service.get_by(**criteria)
        return self._schema.dump(model)

    def parse_and_update(self, model, body, **kwargs):
        form = self._schema_update.load(body, partial=True)
        updated_fields = []
        for name, value in form.items():
            try:
                if getattr(model, name) != value:
                    updated_fields.append(name)
            except AttributeError:
                pass
            setattr(model, name, value)
        self._service.edit(model, updated_fields=updated_fields, **kwargs)

    def update(self, context_id, body, tenant_uuids):
        model = self._service.get(context_id, tenant_uuids=tenant_uuids)
        self.parse_and_update(model, body)