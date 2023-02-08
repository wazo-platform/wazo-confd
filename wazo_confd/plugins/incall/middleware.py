# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.incall import Incall

from .schema import IncallSchema


class IncallMiddleWare:
    def __init__(self, service):
        self._service = service
        self._schema = IncallSchema()

    def create(self, body, tenant_uuid):
        form = self._schema.load(body)
        form['destination'] = Dialaction(**form['destination'])
        form['tenant_uuid'] = tenant_uuid
        model = Incall(**form)
        model = self._service.create(model)
        return self._schema.dump(model)

    def delete(self, incall_id, tenant_uuids):
        model = self._service.get(incall_id, tenant_uuids=tenant_uuids)
        self._service.delete(model)

    def update(self, incall_id, body, tenant_uuids):
        model = self._service.get(incall_id, tenant_uuids=tenant_uuids)
        self.parse_and_update(body, model)

    def parse_and_update(self, body, model):
        form = self._schema.load(body, partial=True)
        updated_fields = self.find_updated_fields(model, form)
        if 'destination' in form:
            form['destination'] = Dialaction(**form['destination'])

        for name, value in form.items():
            setattr(model, name, value)
        self._service.edit(model, updated_fields)

    def find_updated_fields(self, model, form):
        updated_fields = []
        for name, value in form.items():
            try:
                if isinstance(value, dict):
                    if self.find_updated_fields(getattr(model, name), value):
                        updated_fields.append(name)

                elif getattr(model, name) != value:
                    updated_fields.append(name)
            except AttributeError:
                pass
        return updated_fields

    def get(self, incall_id, tenant_uuids):
        model = self._service.get(incall_id, tenant_uuids=tenant_uuids)
        return self._schema.dump(model)
