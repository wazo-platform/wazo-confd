# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.extension import Extension

from .schema import ExtensionSchema


class ExtensionMiddleWare:
    def __init__(self, service):
        self._schema = ExtensionSchema()
        self._service = service

    def create(self, body, tenant_uuids):
        form = self._schema.load(body)
        model = Extension(**form)
        model = self._service.create(model, tenant_uuids)
        return self._schema.dump(model)
