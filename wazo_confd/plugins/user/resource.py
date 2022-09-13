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

    def __init__(
        self,
        user_service,
        line_service,
        extension_service,
        extension_line_service,
        line_endpoint_sip_association_service,
        endpoint_sip_service,
        user_line_service,
        wazo_user_service,
        line_dao,
        sip_dao,
        user_dao,
        transport_dao,
    ):
        self._user_list_resource = UserList(user_service, json_path='user')
        self._line_list_resource = LineList(line_service)
        self._user_line_item_resource = UserLineItem(
            user_line_service, user_dao, line_dao
        )
        self._extension_line_list_resource = LineExtensionList(
            extension_line_service, extension_service, line_dao
        )
        self._endpoint_sip_list_resource = SipList(
            endpoint_sip_service, sip_dao, transport_dao
        )
        self._line_endpoint_sip_association_resource = LineEndpointAssociationSip(
            line_endpoint_sip_association_service, line_dao, sip_dao
        )
        self._line_list_resource.schema = LineSchemaV2
        self._wazo_user_service = wazo_user_service

    def build_headers(self, user):
        return {'Location': url_for('users', id=user['id'], _external=True)}

    @required_acl('confd.users.create')
    def post(self):
        body = UserSchemaV2().load(request.get_json())

        logger.info("Create User resource")
        user_dict, _, _ = self._user_list_resource.post()
        line_list = []

        for line_body in body.get('lines') or []:
            extensions = line_body.pop('extensions', None) or []
            endpoint_sip = line_body.pop('endpoint_sip')
            endpoint_sip, _, _ = self._endpoint_sip_list_resource._post(endpoint_sip)
            line, _, _ = self._line_list_resource._post(line_body)
            self._line_endpoint_sip_association_resource.put(
                line['id'], endpoint_sip['uuid']
            )
            line['endpoint_sip'] = endpoint_sip
            line['extensions'] = []
            for extension_body in extensions:
                extension, _, _ = self._extension_line_list_resource._post(
                    line['id'], extension_body
                )
                line['extensions'].append(extension)
            line_list.append(line)
            self._user_line_item_resource.put(user_dict['id'], line['id'])

        logger.info("Create User authentication")
        # FIX: create(...) takes a user dict containing an 'email_address' key, not an 'email' key
        fixed_user_dict = user_dict.copy()
        fixed_user_dict['email_address'] = fixed_user_dict['email']
        self._wazo_user_service.create(fixed_user_dict)

        return (
            {
                'user': user_dict,
                'lines': line_list,
            },
            201,
            self.build_headers(user_dict),
        )
