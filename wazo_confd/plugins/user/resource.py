# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from flask import request, url_for

from xivo_dao.alchemy.userfeatures import UserFeatures as User

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource
from wazo_confd.plugins.line.resource import LineList
from wazo_confd.plugins.line_endpoint.resource import LineEndpointAssociationSip
from wazo_confd.plugins.extension.resource import ExtensionList
from wazo_confd.plugins.line_extension.resource import LineExtensionList
from wazo_confd.plugins.endpoint_sip.resource import SipList
from wazo_confd.plugins.user_line.resource import UserLineItem

from .schema import (
    UserDirectorySchema,
    UserSchema,
    UserSchemaNullable,
    UserSummarySchema,
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
