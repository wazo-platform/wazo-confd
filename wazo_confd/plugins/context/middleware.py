# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .schema import ContextSchemaPUT
from ...middleware import ResourceMiddleware


class ContextMiddleWare(ResourceMiddleware):
    def __init__(self, service):
        super().__init__(service, ContextSchemaPUT())

    def get(self, **criteria):
        model = self._service.get_by(**criteria)
        return self._schema.dump(model)

    def update(self, context_id, body, tenant_uuids):
        model = self._service.get(context_id, tenant_uuids=tenant_uuids)
        self.parse_and_update(model, body)
