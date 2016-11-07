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

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class GroupExtensionItem(ConfdResource):

    def __init__(self, service, group_dao, extension_dao):
        super(ConfdResource, self).__init__()
        self.service = service
        self.group_dao = group_dao
        self.extension_dao = extension_dao

    @required_acl('confd.groups.{group_id}.extensions.{extension_id}.delete')
    def delete(self, group_id, extension_id):
        group = self.group_dao.get(group_id)
        extension = self.extension_dao.get(extension_id)
        self.service.dissociate(group, extension)
        return '', 204

    @required_acl('confd.groups.{group_id}.extensions.{extension_id}.update')
    def put(self, group_id, extension_id):
        group = self.group_dao.get(group_id)
        extension = self.extension_dao.get(extension_id)
        self.service.associate(group, extension)
        return '', 204
