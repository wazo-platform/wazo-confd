# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from flask import url_for
from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ListResource, ItemResource
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk


class TrunkSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    context = fields.String(required=True)
    links = ListLink(Link('trunks'))


class TrunkList(ListResource):

    model = Trunk
    schema = TrunkSchema()

    def build_headers(self, trunk):
        return {'Location': url_for('trunks', id=trunk.id, _external=True)}

    @required_acl('confd.trunks.create')
    def post(self):
        return super(TrunkList, self).post()

    @required_acl('confd.trunks.read')
    def get(self):
        return super(TrunkList, self).get()


class TrunkItem(ItemResource):

    schema = TrunkSchema()

    @required_acl('confd.trunks.{id}.read')
    def get(self, id):
        return super(TrunkItem, self).get(id)

    @required_acl('confd.trunks.{id}.update')
    def put(self, id):
        return super(TrunkItem, self).put(id)

    @required_acl('confd.trunks.{id}.delete')
    def delete(self, id):
        return super(TrunkItem, self).delete(id)
