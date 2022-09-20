# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from flask import request, url_for

from xivo_dao.alchemy.userfeatures import UserFeatures as User

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource
from wazo_confd.plugins.line.resource import LineList
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

    def __init__(
        self,
        user_service,
        line_service,
        user_line_service,
        endpoint_custom_service,
        endpoint_sip_service,
        extension_line_service,
        extension_service,
        line_endpoint_custom_association_service,
        line_endpoint_sip_association_service,
        line_endpoint_sccp_association_service,
        endpoint_sccp_service,
        wazo_user_service,
        endpoint_custom_dao,
        endpoint_sccp_dao,
        line_dao,
        user_dao,
        sip_dao,
        transport_dao,
    ):
        super().__init__(user_service)
        self._line_list_resource = LineList(
            line_service,
            endpoint_custom_service,
            endpoint_sip_service,
            extension_line_service,
            extension_service,
            line_endpoint_custom_association_service,
            line_endpoint_sip_association_service,
            line_endpoint_sccp_association_service,
            endpoint_sccp_service,
            endpoint_custom_dao,
            endpoint_sccp_dao,
            line_dao,
            sip_dao,
            transport_dao,

        )
        self._user_line_item_resource = UserLineItem(
            user_line_service, user_dao, line_dao
        )
        self._wazo_user_service = wazo_user_service

    def build_headers(self, user):
        return {'Location': url_for('users', id=user.id, _external=True)}

    @required_acl('confd.users.create')
    def post(self):
        return super().post()

    def _post(self, body):
        body = self.schema().load(body)
        lines = body.pop('lines', None) or []

        user_dict, _, headers = super()._post(body)
        user_dict['lines'] = []

        for line_body in lines:
            line, _, _ = self._line_list_resource._post(line_body)
            self._user_line_item_resource.put(user_dict['uuid'], line['id'])
            user_dict['lines'].append(line)

        # FIX: create(...) takes a user dict containing an 'email_address' key, not an 'email' key
        fixed_user_dict = user_dict.copy()
        fixed_user_dict['email_address'] = fixed_user_dict['email']
        self._wazo_user_service.create(fixed_user_dict)
        return user_dict, 201, headers

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
