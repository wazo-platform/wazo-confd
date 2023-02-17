# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.usercustom import UserCustom as Custom

from .schema import CustomSchema


class EndpointCustomMiddleWare:
    def __init__(self, service):
        self._service = service
        self._schema = CustomSchema()

    def create(self, body, tenant_uuid):
        form = self._schema.load(body)
        form['tenant_uuid'] = tenant_uuid
        model = Custom(**form)
        model = self._service.create(model)
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
        return updated_fields

    def update(self, endpoint_custom_id, body, tenant_uuids):
        model = self._service.get(endpoint_custom_id, tenant_uuids=tenant_uuids)
        self.parse_and_update(model, body)
