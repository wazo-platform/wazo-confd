# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from flask import request
from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource


class TrunkSchemaIDLoad(BaseSchema):
    id = fields.Integer(required=True)


class TrunksSchema(BaseSchema):
    trunks = fields.Nested(TrunkSchemaIDLoad, many=True, required=True)


class OutcallTrunkList(ConfdResource):

    schema = TrunksSchema

    def __init__(self, service, outcall_dao, trunk_dao):
        super(OutcallTrunkList, self).__init__()
        self.service = service
        self.outcall_dao = outcall_dao
        self.trunk_dao = trunk_dao

    @required_acl('confd.outcalls.{outcall_id}.trunks.update')
    def put(self, outcall_id):
        form = self.schema().load(request.get_json()).data
        outcall = self.outcall_dao.get(outcall_id)
        trunks = [self.trunk_dao.get(ot['id']) for ot in form['trunks']]
        self.service.associate_all_trunks(outcall, trunks)
        return '', 204
