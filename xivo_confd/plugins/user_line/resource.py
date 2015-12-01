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

from flask import url_for
from flask_restful import reqparse, fields, marshal

from xivo_confd.helpers.restful import FieldList, Link, \
    ListResource, ItemResource


fields = {
    'user_id': fields.Integer,
    'line_id': fields.Integer,
    'main_user': fields.Boolean,
    'main_line': fields.Boolean,
    'links': FieldList(Link('lines',
                            field='line_id',
                            target='id'),
                       Link('users',
                            field='user_id',
                            target='id'))
}

parser = reqparse.RequestParser()
parser.add_argument('line_id', type=int, required=True)


class UserLineList(ListResource):

    def get(self, user_id):
        self.service.validate_parent(user_id)
        items = self.service.list(user_id)
        return {'total': len(items),
                'items': [marshal(item, fields) for item in items]}

    def post(self, user_id):
        form = parser.parse_args()
        user = self.service.validate_parent(user_id)
        line = self.service.validate_resource(form['line_id'])

        user_line = self.service.associate(user, line)

        return marshal(user_line, fields), 201, self.build_headers(user_line)

    def build_headers(self, model):
        url = url_for('user_lines',
                      user_id=model.user_id,
                      line_id=model.line_id,
                      _external=True)
        return {'Location': url}


class UserLineItem(ItemResource):

    def get(self, user_id, line_id):
        self.service.validate_parent(user_id)
        self.service.validate_resource(line_id)
        user_line = self.service.get(user_id, line_id)
        return marshal(user_line, fields)

    def delete(self, user_id, line_id):
        user = self.service.validate_parent(user_id)
        line = self.service.validate_resource(line_id)
        self.service.dissociate(user, line)
        return '', 204


class LineUserList(ListResource):

    def get(self, line_id):
        self.service.validate_resource(line_id)
        items = self.service.list_by_line(line_id)
        return {'total': len(items),
                'items': [marshal(item, fields) for item in items]}
