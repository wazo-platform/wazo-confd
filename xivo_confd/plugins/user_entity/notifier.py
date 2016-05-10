# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_confd import bus
from xivo_bus.resources.user_entity.event import UserEntityAssociatedEvent


class UserEntityNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, user, entity):
        event = UserEntityAssociatedEvent(user.uuid, entity.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return UserEntityNotifier(bus)
