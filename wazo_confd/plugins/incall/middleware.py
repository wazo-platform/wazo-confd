# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
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
