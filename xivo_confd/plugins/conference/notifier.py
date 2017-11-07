# -*- coding: UTF-8 -*-

# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.conference.event import (CreateConferenceEvent,
                                                 EditConferenceEvent,
                                                 DeleteConferenceEvent)


class ConferenceNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['module reload app_confbridge.so'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, conference):
        self.send_sysconfd_handlers()
        event = CreateConferenceEvent(conference.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, conference):
        self.send_sysconfd_handlers()
        event = EditConferenceEvent(conference.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, conference):
        self.send_sysconfd_handlers()
        event = DeleteConferenceEvent(conference.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return ConferenceNotifier(bus, sysconfd)
