# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers.db_manager import Session
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.resources.switchboard import dao as switchboard_dao

from .schema import UserListItemSchema


class UserMiddleWare:
    def __init__(self, service, wazo_user_service, middleware_handle):
        self._service = service
        self._wazo_user_service = wazo_user_service
        self._middleware_handle = middleware_handle
        self._schema = UserListItemSchema()

    def create(self, body, tenant_uuid, tenant_uuids):
        form = self._schema.load(body)
        form['tenant_uuid'] = tenant_uuid

        auth = form.pop('auth', None)
        lines = form.pop('lines', None) or []
        incalls = form.pop('incalls', None) or []
        groups = form.pop('groups', None) or []
        switchboards = form.pop('switchboards', None) or []

        model = User(**form)
        model = self._service.create(model)
        user_dict = self._schema.dump(model)
        user_dict['lines'] = []
        user_dict['incalls'] = []
        user_dict['groups'] = []
        user_dict['switchboards'] = []

        if lines:
            for line_body in lines:
                line = self._middleware_handle.get('line').create(
                    line_body, tenant_uuid, tenant_uuids
                )
                self._middleware_handle.get('user_line_association').associate(
                    user_dict['id'], line['id'], tenant_uuids
                )
                user_dict['lines'].append(line)
            Session.expire(model, ['user_lines'])

        for incall_body in incalls:
            incall = self._middleware_handle.get('incall').create(
                {'destination': {'type': 'user', 'user_id': user_dict['id']}},
                tenant_uuid,
            )
            incall_body['id'] = incall['id']
            user_dict['incalls'].append(incall_body)

            for extension in incall_body['extensions']:
                did_extension_body = {
                    'context': extension['context'],
                    'exten': extension['exten'],
                }
                did_extension = self._middleware_handle.get('extension').create(
                    did_extension_body, tenant_uuids
                )
                extension['id'] = did_extension['id']

                self._middleware_handle.get('incall_extension_association').associate(
                    incall['id'], did_extension['id'], tenant_uuids
                )

        if groups:
            self._middleware_handle.get('user_group_association').associate_all_groups(
                {'groups': groups}, user_dict['uuid']
            )
        user_dict['groups'] = groups

        for _switchboard in switchboards:
            # retrieve the switchboard to add the new user to its members
            switchboard = switchboard_dao.get(
                _switchboard['uuid'], tenant_uuids=tenant_uuids
            )
            members = []
            for user_member in switchboard.user_members:
                members.append({'uuid': user_member.user.uuid})
            members.append({'uuid': user_dict['uuid']})
            self._middleware_handle.get('switchboard_member').associate(
                {'users': members}, _switchboard['uuid'], tenant_uuids
            )
        user_dict['switchboards'] = switchboards

        if auth:
            auth['uuid'] = user_dict['uuid']
            auth['tenant_uuid'] = user_dict['tenant_uuid']
            user_dict['auth'] = self._wazo_user_service.create(auth)

        return user_dict

    def delete(self, user_id, tenant_uuids):
        user = self._service.get(user_id, tenant_uuids=tenant_uuids)
        self._service.delete(user)
