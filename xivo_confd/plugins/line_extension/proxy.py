# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_dao.resources.line_extension.model import LineExtension
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.extension import dao as extension_dao

from xivo_confd.plugins.line_extension import service


class LineExtensionProxyService(object):

    def __init__(self, service, line_dao, extension_dao):
        self.service = service
        self.line_dao = line_dao
        self.extension_dao = extension_dao

    def validate_parent(self, line_id):
        self.line_dao.get(line_id)

    def validate_resource(self, extension_id):
        self.extension_dao.get(extension_id)

    def list(self, line_id):
        return self.service.get_all_by_line_id(line_id)

    def get(self, line_id, extension_id):
        return LineExtension(line_id=line_id, extension_id=extension_id)

    def associate(self, line_extension):
        return self.service.associate(line_extension)

    def dissociate(self, line_extension):
        self.service.dissociate(line_extension)

    def get_by_parent(self, line_id):
        return self.service.get_by_line_id(line_id)

    def get_by_extension_id(self, extension_id):
        return self.service.get_by_extension_id(extension_id)


def build_service():
    return LineExtensionProxyService(service,
                                     line_dao,
                                     extension_dao)
