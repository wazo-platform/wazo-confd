# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from .schema import GroupFallbackSchema


class GroupFallbackList(ConfdResource):

    schema = GroupFallbackSchema

    def __init__(self, service, group_dao):
        super(GroupFallbackList, self).__init__()
        self.service = service
        self.group_dao = group_dao

    @required_acl('confd.groups.{group_id}.fallbacks.read')
    def get(self, group_id):
        group = self.group_dao.get(group_id)
        return self.schema().dump(group.fallbacks).data

    @required_acl('confd.groups.{group_id}.fallbacks.update')
    def put(self, group_id):
        fallbacks = self.schema().load(request.get_json()).data
        group = self.group_dao.get(group_id)
        self.service.edit(group, fallbacks)
        return '', 204
