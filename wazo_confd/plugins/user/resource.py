# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request
import logging


from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo.tenant_flask_helpers import Tenant
from xivo_dao import tenant_dao

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import (
    UserDirectorySchema,
    UserSchema,
    UserListItemSchema,
    UserSummarySchema,
    UserPutSchema,
)

logger = logging.getLogger(__name__)


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
        tenant = Tenant.autodetect()
        tenant_dao.find_or_create_tenant(tenant.uuid)
        tenant_uuids = self._build_tenant_list({'recurse': True})
        resource = self._middleware.create(
            request.get_json(), tenant.uuid, tenant_uuids
        )
        return resource, 201, self.build_headers(resource)

    def _post(self, body):
        body = self.schema().load(body)
        lines = body.pop('lines', None) or []
        auth = body.pop('auth', None)

        user_dict, _, headers = super()._post(body)
        user_dict['lines'] = []

        for line_body in lines:
            line, _, _ = self._line_list_resource._post(line_body)
            self._user_line_item_resource.put(user_dict['uuid'], line['id'])
            user_dict['lines'].append(line)

        if auth:
            auth['uuid'] = user_dict['uuid']
            auth['tenant_uuid'] = user_dict['tenant_uuid']
            user_dict['auth'] = self._wazo_user_service.create(auth)

        return user_dict, 201, headers

    @required_acl('confd.users.read')
    def get(self):
        params = self.search_params()
        tenant_uuids = self._build_tenant_list(params)
        view = params.get('view')
        schema = self.view_schemas.get(view, UserSchema)
        result = self.service.search(params, tenant_uuids)
        return {'total': result.total, 'items': schema().dump(result.items, many=True)}


class UserItem(ItemResource):

    schema = UserPutSchema
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
        return super().put(id)

    @required_acl('confd.users.{id}.delete')
    def delete(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.delete(
            id,
            tenant_uuids,
            recursive=request.args.get(
                'recursive', default=False, type=lambda v: v.lower() == 'true'
            ),
        )
        return '', 204
