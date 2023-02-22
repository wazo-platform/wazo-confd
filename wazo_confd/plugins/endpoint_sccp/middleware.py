# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.sccpline import SCCPLine as SCCPEndpoint

from .schema import SccpSchema
from ...middleware import ResourceMiddleware


class EndpointSCCPMiddleWare(ResourceMiddleware):
    def __init__(self, service):
        super().__init__(service, SccpSchema())

    def create(self, body, tenant_uuid):
        form = self._schema.load(body)
        form['tenant_uuid'] = tenant_uuid
        model = SCCPEndpoint(**form)
        model = self._service.create(model)
        return self._schema.dump(model)

    def update(self, endpoint_sccp_id, body, tenant_uuids):
        model = self._service.get(endpoint_sccp_id, tenant_uuids=tenant_uuids)
        self.parse_and_update(model, body)
