# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean
from xivo_confd.helpers.restful import ConfdResource


class LiveReloadSchema(BaseSchema):
    enabled = StrictBoolean(required=True)


class LiveReloadResource(ConfdResource):

    schema = LiveReloadSchema

    def __init__(self, service):
        super(LiveReloadResource, self).__init__()
        self.service = service

    @required_acl('confd.configuration.live_reload.read')
    def get(self):
        model = self.service.get()
        return self.schema().dump(model).data

    @required_acl('confd.configuration.live_reload.update')
    def put(self):
        form = self.schema().load(request.get_json()).data
        self.service.edit(form)
        return '', 204
