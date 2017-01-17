# -*- coding: UTF-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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
from xivo_confd.helpers.restful import ConfdResource

from .schema import UserFallbackSchema


class UserFallbackList(ConfdResource):

    schema = UserFallbackSchema

    def __init__(self, service, user_dao):
        super(UserFallbackList, self).__init__()
        self.service = service
        self.user_dao = user_dao

    @required_acl('confd.users.{user_id}.fallbacks.read')
    def get(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        return self.schema().dump(user.fallbacks).data

    @required_acl('confd.users.{user_id}.fallbacks.update')
    def put(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        fallbacks = self.schema().load(request.get_json()).data
        self.service.edit(user, fallbacks)
        return '', 204
