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

from xivo_bus.resources.common.event import ArbitraryEvent

from xivo_confd import bus, sysconfd


class MohNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['moh reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, moh):
        self.send_sysconfd_handlers()
        event = ArbitraryEvent(u'moh_created', {u'uuid': moh.uuid})
        self.bus.send_bus_event(event, 'config.moh.created')

    def edited(self, moh):
        self.send_sysconfd_handlers()
        event = ArbitraryEvent(u'moh_edited', {u'uuid': moh.uuid})
        self.bus.send_bus_event(event, 'config.moh.edited')

    def deleted(self, moh):
        self.send_sysconfd_handlers()
        event = ArbitraryEvent(u'moh_deleted', {u'uuid': moh.uuid})
        self.bus.send_bus_event(event, 'config.moh.deleted')

    def files_changed(self, moh):
        self.send_sysconfd_handlers()


def build_notifier():
    return MohNotifier(bus, sysconfd)
