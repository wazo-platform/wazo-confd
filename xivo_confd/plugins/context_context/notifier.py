# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.context_context.event import ContextContextsAssociatedEvent

from xivo_confd import bus


class ContextContextNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated_contexts(self, context, contexts):
        context_ids = [context.id for context in contexts]
        event = ContextContextsAssociatedEvent(context.id, context_ids)
        self.bus.send_bus_event(event)


def build_notifier():
    return ContextContextNotifier(bus)
