# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_confd import sysconfd


class LineDeviceNotifier(object):

    REQUEST_HANDLERS = {'dird': [],
                        'ipbx': ['module reload chan_sccp.so'],
                        'agentbus': [],
                        'ctibus': []}

    def __init__(self, sysconfd):
        self.sysconfd = sysconfd

    def associated(self, line, device):
        self.reload_sccp(line)

    def dissociated(self, line, device):
        self.reload_sccp(line)

    def reload_sccp(self, line):
        if line.endpoint == "sccp":
            self.sysconfd.exec_request_handlers(self.REQUEST_HANDLERS)


def build_notifier():
    return LineDeviceNotifier(sysconfd)
