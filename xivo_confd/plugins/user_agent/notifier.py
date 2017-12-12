# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus
from xivo_bus.resources.user_agent.event import (
    UserAgentAssociatedEvent,
    UserAgentDissociatedEvent,
)


class UserAgentNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, user, agent):
        event = UserAgentAssociatedEvent(user.uuid, agent.id)
        self.bus.send_bus_event(event)

    def dissociated(self, user, agent):
        event = UserAgentDissociatedEvent(user.uuid, agent.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return UserAgentNotifier(bus)
