# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo_dao.alchemy.userfeatures import UserFeatures as User

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import (
    ListResource,
    ItemResource,
    build_tenant,
    is_recursive,
)

from .schema import (
    UserDirectorySchema,
    UserSchema,
    UserListItemSchema,
    UserSummarySchema,
)


class UserList(ListResource):
    model = User
    schema = UserListItemSchema
    view_schemas = {'directory': UserDirectorySchema, 'summary': UserSummarySchema}

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    def build_headers(self, user):
        return {'Location': url_for('users', id=user['id'], _external=True)}

    @required_acl('confd.users.create')
    def post(self):
        tenant_uuid = build_tenant()
        tenant_uuids = self._build_tenant_list({'recurse': True})
        resource = self._middleware.create(
            request.get_json(), tenant_uuid, tenant_uuids
        )
        return resource, 201, self.build_headers(resource)

    @required_acl('confd.users.read')
    def get(self):
        params = self.search_params()
        tenant_uuids = self._build_tenant_list(params)
        view = params.get('view')
        schema = self.view_schemas.get(view, UserSchema)
        result = self.service.search(params, tenant_uuids, is_db_sort_limit=False)
        return {'total': result.total, 'items': schema().dump(result.items, many=True)}


class UserItem(ItemResource):
    schema = UserSchema
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    @required_acl('confd.users.{id}.read')
    def head(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self.service.get(id, tenant_uuids=tenant_uuids)
        return '', 200

    @required_acl('confd.users.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.users.{id}.update')
    def put(self, id):
        tenant_uuid = build_tenant()
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.update(
            id,
            request.get_json(),
            tenant_uuid,
            tenant_uuids,
            recursive=is_recursive(),
        )
        return '', 204

    @required_acl('confd.users.{id}.delete')
    def delete(self, id):
        tenant_uuid = build_tenant()
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.delete(
            id,
            tenant_uuid,
            tenant_uuids,
            recursive=is_recursive(),
        )
        return '', 204
