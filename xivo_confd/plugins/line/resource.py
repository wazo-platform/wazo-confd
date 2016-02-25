# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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
from flask_restful import reqparse, inputs, fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import FieldList, Link, DigitStr, \
    ListResource, ItemResource, Strict
from xivo_dao.alchemy.linefeatures import LineFeatures as Line


line_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'protocol': fields.String,
    'device_slot': fields.Integer,
    'device_id': fields.String,
    'context': fields.String,
    'provisioning_code': fields.String,
    'provisioning_extension': fields.String,
    'position': fields.Integer,
    'caller_id_name': fields.String,
    'caller_id_num': fields.String,
    'links': FieldList(Link('lines'))
}


class LineList(ListResource):

    model = Line

    fields = line_fields

    parser = reqparse.RequestParser()
    parser.add_argument('context', required=True)
    parser.add_argument('provisioning_code', type=DigitStr(6))
    parser.add_argument('position', type=inputs.positive, store_missing=False)
    parser.add_argument('caller_id_name', type=Strict(unicode), store_missing=False)
    parser.add_argument('caller_id_num', type=DigitStr(), store_missing=False)

    def build_headers(self, line):
        return {'Location': url_for('lines', id=line.id, _external=True)}

    @required_acl('confd.lines.read')
    def get(self):
        return super(LineList, self).get()

    @required_acl('confd.lines.create')
    def post(self):
        return super(LineList, self).post()


class LineItem(ItemResource):

    fields = line_fields

    parser = reqparse.RequestParser()
    parser.add_argument('context', store_missing=False)
    parser.add_argument('provisioning_code', type=DigitStr(6), store_missing=False, nullable=False)
    parser.add_argument('position', type=inputs.positive, store_missing=False, nullable=False)
    parser.add_argument('caller_id_name', type=Strict(unicode), store_missing=False)
    parser.add_argument('caller_id_num', type=DigitStr(), store_missing=False)

    @required_acl('confd.lines.{id}.read')
    def get(self, id):
        return super(LineItem, self).get(id)

    @required_acl('confd.lines.{id}.update')
    def put(self, id):
        return super(LineItem, self).put(id)

    @required_acl('confd.lines.{id}.delete')
    def delete(self, id):
        return super(LineItem, self).delete(id)
