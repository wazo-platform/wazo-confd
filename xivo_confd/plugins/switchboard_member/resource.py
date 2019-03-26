# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import UsersUUIDSchema
from xivo_confd.helpers.restful import ConfdResource


class SwitchboardMemberUserItem(ConfdResource):

    schema = UsersUUIDSchema
    has_tenant_uuid = True

    def __init__(self, service, switchboard_dao, user_dao):
        super(SwitchboardMemberUserItem, self).__init__()
        self.service = service
        self.switchboard_dao = switchboard_dao
        self.user_dao = user_dao

    @required_acl('confd.switchboards.{switchboard_uuid}.members.users.update')
    def put(self, switchboard_uuid):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        switchboard = self.switchboard_dao.get(switchboard_uuid, tenant_uuids=tenant_uuids)
        form = self.schema().load(request.get_json()).data
        try:
            users = [self.user_dao.get_by(uuid=user['uuid'], tenant_uuids=tenant_uuids)
                     for user in form['users']]
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_all_member_users(switchboard, users)

        return '', 204
