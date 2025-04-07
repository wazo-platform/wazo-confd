# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.usercustom import UserCustom as Custom

from ...middleware import ResourceMiddleware
from .schema import CustomSchema


class EndpointCustomMiddleWare(ResourceMiddleware):
    def __init__(self, service):
        super().__init__(service, CustomSchema())

    def create(self, body, tenant_uuid):
        form = self._schema.load(body)
        form['tenant_uuid'] = tenant_uuid
        model = Custom(**form)
        model = self._service.create(model)
        return self._schema.dump(model)

    def update(self, endpoint_custom_id, body, tenant_uuids):
        model = self._service.get(endpoint_custom_id, tenant_uuids=tenant_uuids)
        self.parse_and_update(model, body)
