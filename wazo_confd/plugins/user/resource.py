# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from flask import request, url_for

from xivo_dao.alchemy.userfeatures import UserFeatures as User

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource
from wazo_confd.plugins.line.resource import LineListV2

from wazo_confd.plugins.line.schema import LineSchemaV2

from .schema import (
    UserDirectorySchema,
    UserSchema,
    UserSchemaNullable,
    UserSummarySchema,
    UserSchemaV2,
)

logger = logging.getLogger(__name__)


class UserList(ListResource):

    model = User
    schema = UserSchemaNullable
    view_schemas = {'directory': UserDirectorySchema, 'summary': UserSummarySchema}

    def build_headers(self, user):
        return {'Location': url_for('users', id=user.id, _external=True)}

    @required_acl('confd.users.create')
    def post(self):
        return super().post()

    @required_acl('confd.users.read')
    def get(self):
        params = self.search_params()
        tenant_uuids = self._build_tenant_list(params)
        view = params.get('view')
        schema = self.view_schemas.get(view, self.schema)
        result = self.service.search(params, tenant_uuids)
        return {'total': result.total, 'items': schema().dump(result.items, many=True)}


class UserItem(ItemResource):

    schema = UserSchema
    has_tenant_uuid = True

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
        return super().put(id)

    @required_acl('confd.users.{id}.delete')
    def delete(self, id):
        return super().delete(id)


class UserListV2(ListResource):

    api_version = '2.0'

    def __init__(self, user_service, line_service, wazo_user_service):
        self.user_list_resource = UserList(user_service, json_path='user')
        self.line_list_resource = LineListV2(line_service, json_path='lines', many=True)
        self.line_list_resource.schema = LineSchemaV2
        self.wazo_user_service = wazo_user_service

    def build_headers(self, user):
        return {'Location': url_for('users', id=user['id'], _external=True)}

    @required_acl('confd.users.create')
    def post(self):
        body = UserSchemaV2().load(request.get_json())

        logger.info("Create User resource")
        user_dict, _, _ = self.user_list_resource.post()
        if 'lines' in body:
            lines_list, _, _ = self.line_list_resource.post()
        else:
            lines_list = []

        logger.info("Create User authentication")
        # FIX: create(...) takes a user dict containing an 'email_address' key, not an 'email' key
        fixed_user_dict = user_dict.copy()
        fixed_user_dict['email_address'] = fixed_user_dict['email']
        self.wazo_user_service.create(fixed_user_dict)

        return (
            {
                'user': user_dict,
                'lines': lines_list,
            },
            201,
            self.build_headers(user_dict),
        )
