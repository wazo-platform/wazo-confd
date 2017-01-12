# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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

import logging

from xivo_confd import bus

from xivo_bus.resources.common.event import ArbitraryEvent

logger = logging.getLogger(__name__)


class SwitchboardMemberUserNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def members_associated(self, switchboard, users):
        name = 'switchboard_member_user_associated'
        routing_key = 'config.switchboards.{switchboard.id}.members.users.updated'
        acl = 'switchboards.{switchboard.id}.members.users.updated'
        body = {'switchboard_id': switchboard.id,
                'users': [{'uuid': user.uuid} for user in users]}
        event = ArbitraryEvent(name, body, acl)

        self.bus.send_bus_event(event, routing_key.format(switchboard=switchboard))


def build_notifier():
    return SwitchboardMemberUserNotifier(bus)
