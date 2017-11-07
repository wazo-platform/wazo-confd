# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_confd import bus

from xivo_bus.resources.common.event import ArbitraryEvent

logger = logging.getLogger(__name__)


class SwitchboardMemberUserNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def members_associated(self, switchboard, users):
        name = 'switchboard_member_user_associated'
        routing_key = 'config.switchboards.{switchboard.uuid}.members.users.updated'
        acl = 'switchboards.{switchboard.uuid}.members.users.updated'
        body = {'switchboard_uuid': switchboard.uuid,
                'users': [{'uuid': user.uuid} for user in users]}
        event = ArbitraryEvent(name, body, acl)

        self.bus.send_bus_event(event, routing_key.format(switchboard=switchboard))


def build_notifier():
    return SwitchboardMemberUserNotifier(bus)
