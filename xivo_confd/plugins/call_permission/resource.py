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
from flask_restful import reqparse, fields, marshal

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import FieldList, Link, ListResource, ItemResource, Strict
from xivo_dao.alchemy.rightcall import RightCall as CallPermission


call_permission_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'password': fields.String,
    'description': fields.String,
    'mode': fields.String,
    'enabled': fields.Boolean,
    'extensions': fields.List(fields.String),
    'links': FieldList(Link('callpermissions'))
}

parser = reqparse.RequestParser()
parser.add_argument('name', type=Strict(unicode), store_missing=False, nullable=False)
parser.add_argument('password', type=Strict(unicode), store_missing=False)
parser.add_argument('description', type=Strict(unicode), store_missing=False)
parser.add_argument('mode', type=Strict(unicode), store_missing=False, nullable=False)
parser.add_argument('enabled', type=Strict(bool), store_missing=False, nullable=False)
parser.add_argument('extensions', type=Strict(unicode), action='append', store_missing=False, nullable=False)


class CallPermissionList(ListResource):

    model = CallPermission
    fields = call_permission_fields
    parser = parser

    def build_headers(self, call_permission):
        return {'Location': url_for('callpermissions', id=call_permission.id, _external=True)}

    @required_acl('confd.callpermissions.create')
    def post(self):
        return super(CallPermissionList, self).post()

    @required_acl('confd.callpermissions.read')
    def get(self):
        params = self.search_params()
        result = self.service.search(params)

        return {'total': result.total,
                'items': [marshal(item, self.fields) for item in result.items]}


class CallPermissionItem(ItemResource):

    fields = call_permission_fields
    parser = parser

    @required_acl('confd.callpermissions.{id}.read')
    def get(self, id):
        return super(CallPermissionItem, self).get(id)

    @required_acl('confd.callpermissions.{id}.update')
    def put(self, id):
        return super(CallPermissionItem, self).put(id)

    @required_acl('confd.callpermissions.{id}.delete')
    def delete(self, id):
        return super(CallPermissionItem, self).delete(id)
