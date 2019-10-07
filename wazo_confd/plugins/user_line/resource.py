# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request
from marshmallow import EXCLUDE, fields

from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.helpers import errors

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink
from wazo_confd.helpers.restful import ConfdResource


class UserLineSchema(BaseSchema):
    user_id = fields.Integer(dump_only=True)
    line_id = fields.Integer(required=True)
    main_user = fields.Boolean(dump_only=True)
    main_line = fields.Boolean(dump_only=True)
    links = ListLink(
        Link('lines', field='line_id', target='id'),
        Link('users', field='user_id', target='id'),
    )


class LineSchemaIDLoad(BaseSchema):
    id = fields.Integer(required=True)


class LinesIDSchema(BaseSchema):
    lines = fields.Nested(LineSchemaIDLoad, many=True, required=True, unknown=EXCLUDE)


class UserLineResource(ConfdResource):
    def __init__(self, service, user_dao, line_dao):
        super(UserLineResource, self).__init__()
        self.service = service
        self.user_dao = user_dao
        self.line_dao = line_dao

    def get_user(self, user_id, tenant_uuids=None):
        return self.user_dao.get_by_id_uuid(user_id, tenant_uuids)


class UserLineList(UserLineResource):

    deprecated_schema = UserLineSchema
    schema = LinesIDSchema

    @required_acl('confd.users.{user_id}.lines.read')
    def get(self, user_id):
        user = self.get_user(user_id)
        items = self.service.find_all_by(user_id=user.id)
        return {
            'total': len(items),
            'items': self.deprecated_schema().dump(items, many=True),
        }

    @required_acl('confd.users.{user_id}.lines.update')
    def put(self, user_id):
        user = self.get_user(user_id)
        form = self.schema().load(request.get_json())
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
        return (
            self.deprecated_schema().dump(user_line),
            201,
            self.build_headers(user_line),
        )

    def get_line_or_fail(self):
        form = self.deprecated_schema().load(request.get_json())
        try:
            return self.line_dao.get(form['line_id'])
        except NotFoundError:
            raise errors.param_not_found('line_id', 'Line')

    def build_headers(self, model):
        url = url_for(
            'user_lines', user_id=model.user_id, line_id=model.line_id, _external=True
        )
        return {'Location': url}


class UserLineItem(UserLineResource):

    has_tenant_uuid = True

    @required_acl('confd.users.{user_id}.lines.{line_id}.delete')
    def delete(self, user_id, line_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        user = self.get_user(user_id, tenant_uuids=tenant_uuids)
        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)

        self.service.dissociate(user, line)
        return '', 204

    @required_acl('confd.users.{user_id}.lines.{line_id}.update')
    def put(self, user_id, line_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        user = self.get_user(user_id, tenant_uuids=tenant_uuids)
        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)

        self.service.associate(user, line)
        return '', 204


class LineUserList(UserLineResource):

    schema = UserLineSchema

    @required_acl('confd.lines.{line_id}.users.read')
    def get(self, line_id):
        line = self.line_dao.get(line_id)
        items = self.service.find_all_by(line_id=line.id)
        return {'total': len(items), 'items': self.schema().dump(items, many=True)}
