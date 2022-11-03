# Copyright 2022 The Wazo Authors  (see the AUTHORS file)
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
