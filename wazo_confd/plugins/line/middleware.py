# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.linefeatures import LineFeatures as Line

from .schema import LineSchemaNullable


class LineMiddleWare:

    def __init__(self, service):
        self._service = service
        self._schema = LineSchemaNullable()

    def create(self, body, tenant_uuids):
        form = self._schema.load(body)
        model = Line(**form)
        model = self._service.create(model, tenant_uuids)
        return self._schema.dump(model)
