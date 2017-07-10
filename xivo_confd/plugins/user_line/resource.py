# -*- coding: UTF-8 -*-

# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
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

from flask import url_for, request
from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ConfdResource


class UserLineSchema(BaseSchema):
    user_id = fields.Integer(dump_only=True)
    line_id = fields.Integer(required=True)
    main_user = fields.Boolean(dump_only=True)
    main_line = fields.Boolean(dump_only=True)
    links = ListLink(Link('lines',
                          field='line_id',
                          target='id'),
                     Link('users',
                          field='user_id',
                          target='id'))


class LineSchemaIDLoad(BaseSchema):
    id = fields.Integer(required=True)


class LinesIDSchema(BaseSchema):
    lines = fields.Nested(LineSchemaIDLoad, many=True, required=True)


class UserLineResource(ConfdResource):

    def __init__(self, service, user_dao, line_dao):
        super(UserLineResource, self).__init__()
        self.service = service
        self.user_dao = user_dao
        self.line_dao = line_dao

    def get_user(self, user_id):
        return self.user_dao.get_by_id_uuid(user_id)


class UserLineList(UserLineResource):

    deprecated_schema = UserLineSchema
    schema = LinesIDSchema

    @required_acl('confd.users.{user_id}.lines.read')
    def get(self, user_id):
        user = self.get_user(user_id)
        items = self.service.find_all_by(user_id=user.id)
        return {'total': len(items),
                'items': self.deprecated_schema().dump(items, many=True).data}

    @required_acl('confd.users.{user_id}.lines.update')
    def put(self, user_id):
        user = self.get_user(user_id)
        form = self.schema().load(request.get_json()).data
        try:
            lines = [self.line_dao.get(line['id']) for line in form['lines']]
        except NotFoundError as e:
            raise errors.param_not_found('lines', 'Line', **e.metadata)

        self.service.associate_all_lines(user, lines)
        return '', 204

    @required_acl('confd.users.{user_id}.lines.create')
    def post(self, user_id):
        return self._post_deprecated(user_id)

    def _post_deprecated(self, user_id):
        user = self.get_user(user_id)
        line = self.get_line_or_fail()
        user_line = self.service.associate(user, line)
        return self.deprecated_schema().dump(user_line).data, 201, self.build_headers(user_line)

    def get_line_or_fail(self):
        form = self.deprecated_schema().load(request.get_json()).data
        try:
            return self.line_dao.get(form['line_id'])
        except NotFoundError:
            raise errors.param_not_found('line_id', 'Line')

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

    @required_acl('confd.users.{user_id}.lines.{line_id}.update')
    def put(self, user_id, line_id):
        user = self.get_user(user_id)
        line = self.line_dao.get(line_id)
        self.service.associate(user, line)
        return '', 204


class LineUserList(UserLineResource):

    schema = UserLineSchema

    @required_acl('confd.lines.{line_id}.users.read')
    def get(self, line_id):
        line = self.line_dao.get(line_id)
        items = self.service.find_all_by(line_id=line.id)
        return {'total': len(items),
                'items': self.schema().dump(items, many=True).data}
