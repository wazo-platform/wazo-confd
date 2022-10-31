# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.sccpline import SCCPLine as SCCPEndpoint

from .schema import SccpSchema


class EndpointSCCPMiddleWare:
    def __init__(self, service):
        self._service = service
        self._schema = SccpSchema()

    def create(self, body, tenant_uuid):
        form = self._schema.load(body)
        form['tenant_uuid'] = tenant_uuid
        model = SCCPEndpoint(**form)
        model = self._service.create(model)
        return self._schema.dump(model)
