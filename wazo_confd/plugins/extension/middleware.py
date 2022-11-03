# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.plugins.extension.schema import ExtensionSchema
from xivo_dao.alchemy.extension import Extension


class ExtensionMiddleWare:
    def __init__(self, service):
        self._service = service
        self._schema = ExtensionSchema()

    def create(self, body, tenant_uuids):
        form = self._schema.load(body)
        model = Extension(**form)
        model = self._service.create(model, tenant_uuids)
        return self._schema.dump(model)
