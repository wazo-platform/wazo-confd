# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import UsersUUIDSchema
from xivo_confd.helpers.restful import ConfdResource

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError


class PagingUserItem(ConfdResource):

    schema = UsersUUIDSchema

    def __init__(self, service, paging_dao, user_dao):
        super(PagingUserItem, self).__init__()
        self.service = service
        self.paging_dao = paging_dao
        self.user_dao = user_dao


class PagingCallerUserItem(PagingUserItem):

    @required_acl('confd.pagings.{paging_id}.callers.users.update')
    def put(self, paging_id):
        paging = self.paging_dao.get(paging_id)
        form = self.schema().load(request.get_json()).data
        try:
            users = [self.user_dao.get_by(uuid=user['uuid']) for user in form['users']]
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_all_caller_users(paging, users)

        return '', 204


class PagingMemberUserItem(PagingUserItem):

    @required_acl('confd.pagings.{paging_id}.members.users.update')
    def put(self, paging_id):
        paging = self.paging_dao.get(paging_id)
        form = self.schema().load(request.get_json()).data
        try:
            users = [self.user_dao.get_by(uuid=user['uuid']) for user in form['users']]
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_all_member_users(paging, users)

        return '', 204
