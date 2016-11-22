# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_confd import bus

from xivo_bus.resources.common.event import ArbitraryEvent
from .schema import SwitchboardSchema


class SwitchboardNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, switchboard):
        event = ArbitraryEvent(name='switchboard_created',
                               body=SwitchboardSchema().dump(switchboard).data,
                               required_acl='switchboards.{id}.created'.format(id=switchboard.id))
        routing_key = 'config.switchboards.{id}.created'.format(id=switchboard.id)
        self.bus.send_bus_event(event, routing_key)

    def edited(self, switchboard):
        event = ArbitraryEvent(name='switchboard_edited',
                               body=SwitchboardSchema().dump(switchboard).data,
                               required_acl='switchboards.{id}.edited'.format(id=switchboard.id))
        routing_key = 'config.switchboards.{id}.edited'.format(id=switchboard.id)
        self.bus.send_bus_event(event, routing_key)

    def deleted(self, switchboard):
        event = ArbitraryEvent(name='switchboard_deleted',
                               body=SwitchboardSchema().dump(switchboard).data,
                               required_acl='switchboards.{id}.deleted'.format(id=switchboard.id))
        routing_key = 'config.switchboards.{id}.deleted'.format(id=switchboard.id)
        self.bus.send_bus_event(event, routing_key)


def build_notifier():
    return SwitchboardNotifier(bus)
