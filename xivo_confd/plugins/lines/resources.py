# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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


from flask import request
from flask_restful import reqparse, inputs, fields, marshal, marshal_with

from xivo_confd.helpers.restful import ConfdResource, FieldList, Link, DigitStr
from xivo_dao.alchemy.linefeatures import LineFeatures as Line


line_fields = {
    'id': fields.Integer,
    'context': fields.String,
    'provisioning_code': fields.String,
    'position': fields.Integer,
    'caller_name': fields.String,
    'caller_num': fields.String,
    'links': FieldList(Link('lines'))
}


class LineResource(ConfdResource):

    def __init__(self, service):
        super(LineResource, self).__init__()
        self.service = service


class LineList(LineResource):

    parser = reqparse.RequestParser()
    parser.add_argument('context', required=True)
    parser.add_argument('provisioning_code', type=DigitStr(6))
    parser.add_argument('position', type=inputs.positive, default=1)
    parser.add_argument('caller_name')
    parser.add_argument('caller_num', type=DigitStr())

    def get(self):
        params = {key: request.args[key] for key in request.args}
        total, items = self.service.search(params)
        return {'total': total,
                'items': [marshal(l, line_fields) for l in items]}

    @marshal_with(line_fields)
    def post(self):
        form = self.parser.parse_args()
        line = Line(**form)
        line = self.service.create(line)
        return line


class LineItem(LineResource):

    parser = reqparse.RequestParser()
    parser.add_argument('context', store_missing=False)
    parser.add_argument('provisioning_code', type=DigitStr(6), store_missing=False)
    parser.add_argument('position', type=inputs.positive, store_missing=False)
    parser.add_argument('caller_name', store_missing=False)
    parser.add_argument('caller_num', type=DigitStr(), store_missing=False)

    @marshal_with(line_fields)
    def get(self, id):
        return self.service.get(id)

    def put(self, id):
        line = self.service.get(id)
        form = self.parser.parse_args()
        for name, value in form.iteritems():
            setattr(line, name, value)
        self.service.edit(line)
        return '', 204

    def delete(self, id):
        line = self.service.get(id)
        self.service.delete(line)
        return '', 204
