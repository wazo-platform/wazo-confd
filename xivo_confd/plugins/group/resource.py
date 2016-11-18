# -*- coding: utf-8 -*-

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

from flask import url_for

from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import GroupSchema


class GroupList(ListResource):

    model = Group
    schema = GroupSchema

    def build_headers(self, group):
        return {'Location': url_for('groups', id=group.id, _external=True)}

    @required_acl('confd.groups.create')
    def post(self):
        return super(GroupList, self).post()

    @required_acl('confd.groups.read')
    def get(self):
        return super(GroupList, self).get()


class GroupItem(ItemResource):

    schema = GroupSchema

    @required_acl('confd.groups.{id}.read')
    def get(self, id):
        return super(GroupItem, self).get(id)

    @required_acl('confd.groups.{id}.update')
    def put(self, id):
        return super(GroupItem, self).put(id)

    @required_acl('confd.groups.{id}.delete')
    def delete(self, id):
        return super(GroupItem, self).delete(id)
