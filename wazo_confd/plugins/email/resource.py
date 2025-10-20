# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl, required_master_tenant
from wazo_confd.helpers.restful import ConfdResource

from .schema import EmailConfigSchema


class EmailConfig(ConfdResource):
    schema = EmailConfigSchema

    def __init__(self, service):
        self.service = service

    @required_master_tenant()
    @required_acl('confd.emails.read')
    def get(self):
        model = self.service.get()
        return self.schema().dump(model)

    @required_master_tenant()
    @required_acl('confd.emails.update')
    def put(self):
        model = self.service.get()
        form = self.schema().load(request.get_json(force=True))
        for name, value in form.items():
            setattr(model, name, value)
        self.service.edit(model)
        return '', 204
