# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import url_for
from marshmallow import fields
from marshmallow.validate import Length

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ListResource, ItemResource
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPEndpoint


class SccpSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    options = fields.List(fields.List(fields.String(), validate=Length(equal=2)))
    links = ListLink(Link('endpoint_sccp'))

    line = fields.Nested('LineSchema', only=['id', 'links'], dump_only=True)


class SccpList(ListResource):

    model = SCCPEndpoint
    schema = SccpSchema

    def build_headers(self, sccp):
        return {'Location': url_for('endpoint_sccp', id=sccp.id, _external=True)}

    @required_acl('confd.endpoints.sccp.read')
    def get(self):
        return super(SccpList, self).get()

    @required_acl('confd.endpoints.sccp.create')
    def post(self):
        return super(SccpList, self).post()


class SccpItem(ItemResource):

    schema = SccpSchema

    @required_acl('confd.endpoints.sccp.{id}.read')
    def get(self, id):
        return super(SccpItem, self).get(id)

    @required_acl('confd.endpoints.sccp.{id}.update')
    def put(self, id):
        return super(SccpItem, self).put(id)

    @required_acl('confd.endpoints.sccp.{id}.delete')
    def delete(self, id):
        return super(SccpItem, self).delete(id)
