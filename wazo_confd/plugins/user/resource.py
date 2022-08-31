# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from flask import request, url_for

from xivo_dao.alchemy.userfeatures import UserFeatures as User

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import (
    UserDirectorySchema,
    UserSchema,
    UserSchemaNullable,
    UserSummarySchema,
    UnifiedUserSchema,
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


class UnifiedUserList(ListResource):

    api_version = '2.0'

    def __init__(self, user_service, wazo_user_service):
        self.user_list_resource = UserList(user_service, json_path='user')
        self.wazo_user_service = wazo_user_service

    def build_headers(self, user):
        return {'Location': url_for('users', id=user['id'], _external=True)}

    @required_acl('confd.users.create')
    def post(self):
        logger.info("Create Unified User NEW")
        UnifiedUserSchema().load(request.get_json())

        logger.info("Create User resource")
        user_dict, _, _ = self.user_list_resource.post()

        logger.info("Create User authentication")
        # FIX: create(...) takes a user dict containing an 'email_address' key, not an 'email' key
        fixed_user_dict = user_dict.copy()
        fixed_user_dict['email_address'] = fixed_user_dict['email']
        self.wazo_user_service.create(fixed_user_dict)

        return (
            {
                'user': user_dict,
            },
            201,
            self.build_headers(user_dict),
        )
