# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError
from xivo_dao.resources.switchboard import dao as switchboard_dao
from xivo_dao.resources.user import dao as user_dao

from wazo_confd.helpers.mallow import UsersUUIDSchema


class SwitchboardMemberMiddleWare:
    def __init__(self, service):
        self._service = service
        self._schema = UsersUUIDSchema()

    def associate(self, body, switchboard_uuid, tenant_uuids):
        """
        Associate a list of users to a switchboard.
        Any existing members of the switchboard are removed before.
        """
        switchboard = switchboard_dao.get(switchboard_uuid, tenant_uuids=tenant_uuids)
        form = self._schema.load(body)
        try:
            users = [
                user_dao.get_by(uuid=user['uuid'], tenant_uuids=tenant_uuids)
                for user in form['users']
            ]
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self._service.associate_all_member_users(switchboard, users)

    def dissociate(self, user_id, switchboard_uuid, tenant_uuids):
        """
        Dissociate a user from a switchboard.
        The other existing members of the switchboard are kept.
        """
        switchboard = switchboard_dao.get(switchboard_uuid, tenant_uuids=tenant_uuids)
        try:
            users = [
                user_dao.get_by(uuid=user_member.uuid, tenant_uuids=tenant_uuids)
                for user_member in switchboard.user_members
                if user_member.uuid != user_id
            ]
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self._service.associate_all_member_users(switchboard, users)

    def associate_user_to_switchboards(self, user_id, switchboards, tenant_uuids):
        """
        Associate a user to switchboards.
        The existing members of the switchboards are kept.
        """
        for _switchboard in switchboards:
            # retrieve the switchboard to add the new user to its members
            switchboard = switchboard_dao.get(
                _switchboard['uuid'], tenant_uuids=tenant_uuids
            )
            members = []
            for user_member in switchboard.user_members:
                members.append({'uuid': user_member.uuid})
            members.append({'uuid': user_id})
            self.associate({'users': members}, _switchboard['uuid'], tenant_uuids)
