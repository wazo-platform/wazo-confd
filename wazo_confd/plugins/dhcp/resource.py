# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from wazo_confd.auth import required_acl, required_master_tenant
from wazo_confd.helpers.restful import ConfdResource

from .schema import DHCPSchema


class DHCPResource(ConfdResource):
    schema = DHCPSchema

    def __init__(self, service):
        self.service = service

    @required_master_tenant()
    @required_acl('confd.dhcp.read')
    def get(self):
        model = self.service.get()
        return self.schema().dump(model)

    @required_master_tenant()
    @required_acl('confd.dhcp.update')
    def put(self):
        form = self.schema().load(request.get_json(force=True))
        self.service.edit(form)
        return '', 204
