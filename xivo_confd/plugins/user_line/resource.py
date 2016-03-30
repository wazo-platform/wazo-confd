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


class UserLineResource(ConfdResource):

    def __init__(self, service, user_dao, line_dao):
        super(ConfdResource, self).__init__()
        self.service = service
        self.user_dao = user_dao
        self.line_dao = line_dao

    def get_line_or_fail(self):
        form = parser.parse_args()
        try:
            return self.line_dao.get(form['line_id'])
        except NotFoundError:
            raise errors.param_not_found('line_id', 'Line')

    def get_user(self, user_id):
        return self.user_dao.get_by_id_uuid(user_id)


class UserLineList(UserLineResource):

    @required_acl('confd.users.{user_id}.lines.read')
    def get(self, user_id):
        user = self.get_user(user_id)
        items = self.service.find_all_by(user_id=user.id)
        return {'total': len(items),
                'items': [marshal(item, fields) for item in items]}

    @required_acl('confd.users.{user_id}.lines.create')
    def post(self, user_id):
        user = self.get_user(user_id)
        line = self.get_line_or_fail()
        user_line = self.service.associate(user, line)

        return marshal(user_line, fields), 201, self.build_headers(user_line)

    def build_headers(self, model):
        url = url_for('user_lines',
                      user_id=model.user_id,
                      line_id=model.line_id,
                      _external=True)
        return {'Location': url}


class UserLineItem(UserLineResource):

    @required_acl('confd.users.{user_id}.lines.{line_id}.delete')
    def delete(self, user_id, line_id):
        user = self.get_user(user_id)
        line = self.line_dao.get(line_id)
        self.service.dissociate(user, line)
        return '', 204


class LineUserList(UserLineResource):

    @required_acl('confd.lines.{line_id}.users.read')
    def get(self, line_id):
        line = self.line_dao.get(line_id)
        items = self.service.find_all_by(line_id=line.id)
        return {'total': len(items),
                'items': [marshal(item, fields) for item in items]}
