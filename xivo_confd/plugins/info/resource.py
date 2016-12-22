# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
