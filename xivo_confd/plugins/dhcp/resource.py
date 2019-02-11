# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource

from .schema import DHCPSchema


class DHCPResource(ConfdResource):

    schema = DHCPSchema

    def __init__(self, service):
        self.service = service

    @required_acl('confd.dhcp.read')
    def get(self):
        model = self.service.get()
        return self.schema().dump(model).data

    @required_acl('confd.dhcp.update')
    def put(self):
        form = self.schema().load(request.get_json()).data
        self.service.edit(form)
        return '', 204
