# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus
from xivo_bus.resources.user_agent.event import (UserAgentAssociatedEvent,
                                                 UserAgentDissociatedEvent)


class UserAgentNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, user, agent):
        event = UserAgentAssociatedEvent(user.uuid, agent.id)
        self.bus.send_bus_event(event, event.routing_key)

    def dissociated(self, user, agent):
        event = UserAgentDissociatedEvent(user.uuid, agent.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return UserAgentNotifier(bus)
