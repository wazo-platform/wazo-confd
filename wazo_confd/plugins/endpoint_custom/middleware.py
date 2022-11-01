# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
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
