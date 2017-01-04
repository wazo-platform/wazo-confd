# -*- coding: UTF-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from flask import request

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import UsersUUIDSchema
from xivo_confd.helpers.restful import ConfdResource


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
        users = [self.user_dao.get_by(uuid=user['uuid']) for user in form['users']]
        self.service.associate_all_caller_users(paging, users)
        return '', 204


class PagingMemberUserItem(PagingUserItem):

    @required_acl('confd.pagings.{paging_id}.members.users.update')
    def put(self, paging_id):
        paging = self.paging_dao.get(paging_id)
        form = self.schema().load(request.get_json()).data
        users = [self.user_dao.get_by(uuid=user['uuid']) for user in form['users']]
        self.service.associate_all_member_users(paging, users)
        return '', 204
