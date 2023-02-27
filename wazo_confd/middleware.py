# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class ResourceMiddleware:
    def __init__(self, service, schema, update_schema=None):
        self._service = service
        self._schema = schema
        self._update_schema = schema if not update_schema else update_schema

    def parse_and_update(self, model, body, **kwargs):
        form = self._update_schema.load(body, partial=True)
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
