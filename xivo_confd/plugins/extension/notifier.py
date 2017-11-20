# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.extension.event import CreateExtensionEvent, \
    EditExtensionEvent, DeleteExtensionEvent


class ExtensionNotifier(object):

    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ctibus': [],
                    'ipbx': ipbx,
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, extension):
        self.send_sysconfd_handlers(['dialplan reload'])
        event = CreateExtensionEvent(extension.id,
                                     extension.exten,
                                     extension.context)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, extension, updated_fields):
        if updated_fields is None or updated_fields:
            self.send_sysconfd_handlers(['dialplan reload',
                                         'sip reload',
                                         'module reload chan_sccp.so',
                                         'module reload app_queue.so'])
        event = EditExtensionEvent(extension.id,
                                   extension.exten,
                                   extension.context)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, extension):
        self.send_sysconfd_handlers(['dialplan reload'])
        event = DeleteExtensionEvent(extension.id,
                                     extension.exten,
                                     extension.context)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return ExtensionNotifier(sysconfd, bus)
