# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.context_context.event import ContextContextsAssociatedEvent

from xivo_confd import bus, sysconfd


class ContextContextNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['dialplan reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated_contexts(self, context, contexts):
        self.send_sysconfd_handlers()
        context_ids = [context.id for context in contexts]
        event = ContextContextsAssociatedEvent(context.id, context_ids)
        self.bus.send_bus_event(event)


def build_notifier():
    return ContextContextNotifier(bus, sysconfd)
