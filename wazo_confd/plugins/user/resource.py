# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from flask import url_for

from xivo_dao.alchemy.userfeatures import UserFeatures as User

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource
from wazo_confd.plugins.line.resource import LineList
from wazo_confd.plugins.user_line.resource import UserLineItem
from wazo_confd.plugins.extension.resource import ExtensionList

from .schema import (
    UserDirectorySchema,
    UserSummarySchema,
    UserItemSchema,
    UserListItemSchema,
)
from ..func_key.resource import UserFuncKeyTemplateAssociation
from ..incall.resource import IncallList
from ..incall_extension.resource import IncallExtensionItem

logger = logging.getLogger(__name__)


class UserList(ListResource):

    model = User
    schema = UserListItemSchema
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
        incall_service,
        incall_extension_service,
        user_group_service,
        user_funckey_template_association_service,
        user_switchboard_service,
        endpoint_custom_dao,
        endpoint_sccp_dao,
        line_dao,
        user_dao,
        sip_dao,
        transport_dao,
        incall_dao,
        extension_dao,
        group_dao,
        template_dao,
        switchboard_dao,
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
        self._user_funckey_template_association_resource = (
            UserFuncKeyTemplateAssociation(
                user_funckey_template_association_service, user_dao, template_dao
            )
        )
        self._wazo_user_service = wazo_user_service
        self._extension_list_resource = ExtensionList(extension_service)
        self._incall_list_resource = IncallList(incall_service)
        self._incall_extension_resource = IncallExtensionItem(
            incall_extension_service, incall_dao, extension_dao
        )
        self._user_group_service = user_group_service
        self._user_switchboard_service = user_switchboard_service
        self._group_dao = group_dao
        self._user_dao = user_dao
        self._template_dao = template_dao
        self._switchboard_dao = switchboard_dao

    def build_headers(self, user):
        return {'Location': url_for('users', id=user.id, _external=True)}

    @required_acl('confd.users.create')
    def post(self):
        return super().post()

    def _post(self, body):
        body = self.schema().load(body)
        lines = body.pop('lines', None) or []
        auth = body.pop('auth', None)
        incalls = body.pop('incalls', None) or []
        groups = body.pop('groups', None) or []
        switchboards = body.pop('switchboards', None) or []
        user_dict, _, headers = super()._post(body)
        user_dict['lines'] = []
        user_dict['incalls'] = []
        user_dict['groups'] = []
        user_dict['switchboards'] = []

        for line_body in lines:
            line, _, _ = self._line_list_resource._post(line_body)
            self._user_line_item_resource.put(user_dict['uuid'], line['id'])
            user_dict['lines'].append(line)

        if auth:
            auth['uuid'] = user_dict['uuid']
            auth['tenant_uuid'] = user_dict['tenant_uuid']
            user_dict['auth'] = self._wazo_user_service.create(auth)

        for incall_body in incalls:

            # create incall (destination.type=user)
            incall, _, _ = self._incall_list_resource._post(
                {'destination': {'type': 'user', 'user_id': user_dict['id']}}
            )
            incall_body['id'] = incall['id']
            user_dict['incalls'].append(incall_body)

            for extension in incall_body['extensions']:

                # create extension (the "source/origin/public/external")
                source_extension_body = {
                    'context': extension['context'],
                    'exten': extension['exten'],
                }
                source_extension, _, _ = self._extension_list_resource._post(
                    source_extension_body
                )
                extension['id'] = source_extension['id']

                # link incall+source extension
                self._incall_extension_resource.put(
                    incall['id'], source_extension['id']
                )

        if groups:
            self._user_group_service.associate_all_groups(
                self._user_dao.get_by_id_uuid(user_dict['id']),
                [self._group_dao.get_by(uuid=group['uuid']) for group in groups],
            )
        user_dict['groups'] = groups

        if switchboards:
            tenant_uuids = self._build_tenant_list({'recurse': True})
            current_user = self._user_dao.get_by_id_uuid(user_dict['id'])

            for _switchboard in switchboards:
                switchboard = self._switchboard_dao.get(
                    _switchboard['uuid'], tenant_uuids=tenant_uuids
                )
                members = []
                for user_member in switchboard.user_members:
                    members.append(user_member.user)
                members.append(current_user)

                self._user_switchboard_service.associate_all_member_users(
                    switchboard, members
                )

        user_dict['switchboards'] = switchboards

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

    schema = UserItemSchema
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
