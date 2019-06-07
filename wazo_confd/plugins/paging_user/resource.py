# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import UsersUUIDSchema
from xivo_confd.helpers.restful import ConfdResource


class PagingUserItem(ConfdResource):

    schema = UsersUUIDSchema
    has_tenant_uuid = True

    def __init__(self, service, paging_dao, user_dao):
        super(PagingUserItem, self).__init__()
        self.service = service
        self.paging_dao = paging_dao
        self.user_dao = user_dao


class PagingCallerUserItem(PagingUserItem):

    @required_acl('confd.pagings.{paging_id}.callers.users.update')
    def put(self, paging_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        paging = self.paging_dao.get(paging_id, tenant_uuids=tenant_uuids)
        form = self.schema().load(request.get_json()).data
        try:
            users = [self.user_dao.get_by(uuid=user['uuid'], tenant_uuids=tenant_uuids) for user in form['users']]
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_all_caller_users(paging, users)

        return '', 204


class PagingMemberUserItem(PagingUserItem):

    @required_acl('confd.pagings.{paging_id}.members.users.update')
    def put(self, paging_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        paging = self.paging_dao.get(paging_id, tenant_uuids=tenant_uuids)
        form = self.schema().load(request.get_json()).data
        try:
            users = [self.user_dao.get_by(uuid=user['uuid'], tenant_uuids=tenant_uuids) for user in form['users']]
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_all_member_users(paging, users)

        return '', 204
