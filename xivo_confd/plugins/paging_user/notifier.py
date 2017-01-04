# -*- coding: utf-8 -*-

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

from xivo_confd import bus
from xivo_bus.resources.paging_user.event import (PagingMemberUsersAssociatedEvent,
                                                  PagingCallerUsersAssociatedEvent)


class PagingUserNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def callers_associated(self, paging, users):
        user_uuids = [user.uuid for user in users]
        event = PagingCallerUsersAssociatedEvent(paging.id, user_uuids)
        self.bus.send_bus_event(event, event.routing_key)

    def members_associated(self, paging, users):
        user_uuids = [user.uuid for user in users]
        event = PagingMemberUsersAssociatedEvent(paging.id, user_uuids)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return PagingUserNotifier(bus)
