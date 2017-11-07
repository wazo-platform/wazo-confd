# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource


class InfoSchema(BaseSchema):
    uuid = fields.UUID()
    wazo_version = fields.String()


class Info(ConfdResource):

    schema = InfoSchema

    def __init__(self, service):
        super(Info, self).__init__()
        self.service = service

    @required_acl('confd.infos.read')
    def get(self):
        info = self.service.get()
        return self.schema().dump(info).data
