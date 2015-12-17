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

from xivo_confd.plugins.line_extension.manager import build_manager
from xivo_confd.plugins.line_extension import notifier


class LineExtensionService(object):

    def __init__(self, manager, notifier):
        self.manager = manager
        self.notifier = notifier

    def list(self, line_id):
        return self.manager.list(line_id)

    def get(self, line, extension):
        return self.manager.get_association(line, extension)

    def associate(self, line, extension):
        line_extension = self.manager.associate(line, extension)
        self.notifier.associated(line_extension)
        return line_extension

    def dissociate(self, line, extension):
        line_extension = self.get(line, extension)
        self.notifier.dissociated(line_extension)
        self.manager.dissociate(line, extension)


def build_service():
    return LineExtensionService(build_manager(),
                                notifier)
