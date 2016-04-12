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

from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers import errors

from flask import url_for
from flask_restful import reqparse, fields, marshal

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import FieldList, Link, ConfdResource


fields = {
    'line_id': fields.Integer,
    'extension_id': fields.Integer,
    'links': FieldList(Link('lines',
                            field='line_id',
                            target='id'),
                       Link('extensions',
                            field='extension_id',
                            target='id'))
}

parser = reqparse.RequestParser()
parser.add_argument('line_id', type=int, required=True, location='view_args')
parser.add_argument('extension_id', type=int, required=True)


class LineExtensionResource(ConfdResource):

    def __init__(self, service, line_dao, extension_dao):
        super(ConfdResource, self).__init__()
        self.service = service
        self.line_dao = line_dao
        self.extension_dao = extension_dao

    def get_extension_or_fail(self):
        form = parser.parse_args()
        try:
            return self.extension_dao.get(form['extension_id'])
        except NotFoundError:
            raise errors.param_not_found('extension_id', 'Extension')


class LineExtensionList(LineExtensionResource):

    @required_acl('confd.lines.{line_id}.extensions.read')
    def get(self, line_id):
        line = self.line_dao.get(line_id)
        items = self.service.list(line.id)
        return {'total': len(items),
                'items': [marshal(item, fields) for item in items]}

    @required_acl('confd.lines.{line_id}.extensions.create')
    def post(self, line_id):
        line = self.line_dao.get(line_id)
        extension = self.get_extension_or_fail()
        line_extension = self.service.associate(line, extension)
        headers = self.build_headers(line_extension)
        return marshal(line_extension, fields), 201, headers

    def build_headers(self, model):
        url = url_for('line_extensions',
                      extension_id=model.extension_id,
                      line_id=model.line_id,
                      _external=True)
        return {'Location': url}


class LineExtensionItem(LineExtensionResource):

    @required_acl('confd.lines.{line_id}.extensions.{extension_id}.delete')
    def delete(self, line_id, extension_id):
        line = self.line_dao.get(line_id)
        extension = self.extension_dao.get(extension_id)
        self.service.dissociate(line, extension)
        return '', 204
