# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema
from wazo_confd.helpers.restful import ConfdResource


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
