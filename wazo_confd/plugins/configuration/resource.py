# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl, required_master_tenant
from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean
from wazo_confd.helpers.restful import ConfdResource


class LiveReloadSchema(BaseSchema):
    enabled = StrictBoolean(required=True)


class LiveReloadResource(ConfdResource):
    schema = LiveReloadSchema

    def __init__(self, service):
        super().__init__()
        self.service = service

    @required_master_tenant()
    @required_acl('confd.configuration.live_reload.read')
    def get(self):
        model = self.service.get()
        return self.schema().dump(model)

    @required_master_tenant()
    @required_acl('confd.configuration.live_reload.update')
    def put(self):
        form = self.schema().load(request.get_json(force=True))
        self.service.edit(form)
        return '', 204
