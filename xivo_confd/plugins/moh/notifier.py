# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
        event.routing_key = 'config.moh.created'
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, moh):
        self.send_sysconfd_handlers()
        event = ArbitraryEvent(u'moh_edited', {u'uuid': moh.uuid})
        event.routing_key = 'config.moh.edited'
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, moh):
        self.send_sysconfd_handlers()
        event = ArbitraryEvent(u'moh_deleted', {u'uuid': moh.uuid})
        event.routing_key = 'config.moh.deleted'
        self.bus.send_bus_event(event, event.routing_key)

    def files_changed(self, moh):
        self.send_sysconfd_handlers()


def build_notifier():
    return MohNotifier(bus, sysconfd)
