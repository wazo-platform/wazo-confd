# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource

from .schema import ProvisioningNetworkingSchema


class ProvisioningNetworkingResource(ConfdResource):

    schema = ProvisioningNetworkingSchema

    def __init__(self, service):
        self.service = service

    @required_acl('confd.provisioning.networking.read')
    def get(self):
        model = self.service.get()
        return self.schema().dump(model).data

    @required_acl('confd.provisioning.networking.update')
    def put(self):
        model = self.service.get()
        form = self.schema().load(request.get_json(), partial=True).data
        for name, value in form.iteritems():
            setattr(model, name, value)
        self.service.edit(model)
        return '', 204
