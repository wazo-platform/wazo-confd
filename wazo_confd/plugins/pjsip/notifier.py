# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.pjsip.event import (
    PJSIPGlobalUpdatedEvent,
    PJSIPSystemUpdatedEvent,
    CreateSIPTransportEvent,
    EditSIPTransportEvent,
    DeleteSIPTransportEvent,
)

from wazo_confd import bus, sysconfd


class PJSIPConfigurationNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, section_name, file_):
        # TODO(pc-m): Adding the variables to the body would avoid a GET
        # from the Sorcery proxy when we implement it
        if section_name == 'global':
            event = PJSIPGlobalUpdatedEvent()
        elif section_name == 'system':
            event = PJSIPSystemUpdatedEvent()
        else:
            return

        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(['module reload res_pjsip.so'])


def build_notifier():
    return PJSIPConfigurationNotifier(bus, sysconfd)


class PJSIPTransportNotifier:
    def __init__(self, bus, sysconfd, schema):
        self.bus = bus
        self.sysconfd = sysconfd
        self.schema = schema

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload res_pjsip.so']}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, transport):
        self.send_sysconfd_handlers()
        body = self.schema.dump(transport)
        event = CreateSIPTransportEvent(body)
        self.bus.send_bus_event(event)

    def deleted(self, transport):
        self.send_sysconfd_handlers()
        body = self.schema.dump(transport)
        event = DeleteSIPTransportEvent(body)
        self.bus.send_bus_event(event)

    def edited(self, transport):
        self.send_sysconfd_handlers()
        body = self.schema.dump(transport)
        event = EditSIPTransportEvent(body)
        self.bus.send_bus_event(event)


def build_pjsip_transport_notifier(schema):
    return PJSIPTransportNotifier(bus, sysconfd, schema)
