# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import fields
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema, Nested
from wazo_confd.helpers.restful import ConfdResource


class LineSchemaIDLoad(BaseSchema):
    id = fields.Integer(required=True)


class LinesIDSchema(BaseSchema):
    lines = Nested(LineSchemaIDLoad, many=True, required=True)


class UserLineResource(ConfdResource):
    def __init__(self, service, user_dao, line_dao):
        super().__init__()
        self.service = service
        self.user_dao = user_dao
        self.line_dao = line_dao

    def get_user(self, user_id, tenant_uuids=None):
        return self.user_dao.get_by_id_uuid(user_id, tenant_uuids)


class UserLineList(UserLineResource):
    schema = LinesIDSchema

    @required_acl('confd.users.{user_id}.lines.update')
    def put(self, user_id):
        user = self.get_user(user_id)
        form = self.schema().load(request.get_json(force=True))
        try:
            lines = [self.line_dao.get(line['id']) for line in form['lines']]
        except NotFoundError as e:
            raise errors.param_not_found('lines', 'Line', **e.metadata)

        self.service.associate_all_lines(user, lines)
        return '', 204


class UserLineItem(UserLineResource):
    has_tenant_uuid = True

    def __init__(self, service, user_dao, line_dao, middleware):
        super().__init__(service, user_dao, line_dao)
        self._middleware = middleware

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
        self._middleware.associate(user_id, line_id, tenant_uuids)

        return '', 204
