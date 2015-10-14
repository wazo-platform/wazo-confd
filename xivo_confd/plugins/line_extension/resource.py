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


from flask_restful import reqparse, fields, marshal

from xivo_dao.resources.line_extension.model import LineExtension

from xivo_confd.helpers.restful import FieldList, Link, \
    ListResource, ItemResource


fields = {
    'line_id': fields.Integer,
    'extension_id': fields.Integer,
    'links': FieldList(Link('lines',
                            field='line_id',
                            target='id'),
                       Link('extensions',
                            route='extensions.get',
                            field='extension_id',
                            target='resource_id'))
}

parser = reqparse.RequestParser()
parser.add_argument('line_id', type=int, required=True, location='view_args')
parser.add_argument('extension_id', type=int, required=True)


class LineExtensionList(ListResource):

    def get(self, line_id):
        self.service.validate_parent(line_id)
        items = self.service.list(line_id)
        return {'total': len(items),
                'items': [marshal(item, fields) for item in items]}

    def post(self, line_id):
        self.service.validate_parent(line_id)
        form = parser.parse_args()
        line_extension = LineExtension(**form)
        line_extension = self.service.associate(line_extension)
        return marshal(line_extension, fields), 201


class LineExtensionItem(ItemResource):

    def get(self, line_id, extension_id):
        self.service.validate_parent(line_id)
        self.service.validate_resource(extension_id)
        line_extension = self.service.get(line_id, extension_id)
        return marshal(line_extension, fields)

    def delete(self, line_id, extension_id):
        self.service.validate_parent(line_id)
        self.service.validate_resource(extension_id)
        line_extension = self.service.get(line_id, extension_id)
        self.service.dissociate(line_extension)
        return '', 204


class LineExtensionLegacy(ItemResource):

    def get(self, line_id):
        self.service.validate_parent(line_id)
        line_extension = self.service.get_by_parent(line_id)
        return marshal(line_extension, fields)

    def post(self, line_id):
        self.service.validate_parent(line_id)
        form = parser.parse_args()
        line_extension = LineExtension(**form)
        line_extension = self.service.associate(line_extension)
        return marshal(line_extension, fields), 201

    def delete(self, line_id):
        self.service.validate_parent(line_id)
        line_extension = self.service.get_by_parent(line_id)
        self.service.dissociate(line_extension)
        return '', 204


class ExtensionLineLegacy(ItemResource):

    def get(self, extension_id):
        self.service.validate_resource(extension_id)
        line_extension = self.service.get_by_extension_id(extension_id)
        return marshal(line_extension, fields)
