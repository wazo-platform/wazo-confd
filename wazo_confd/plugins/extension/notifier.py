# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.extension.event import (
    ExtensionCreatedEvent,
    ExtensionDeletedEvent,
    ExtensionEditedEvent,
)

from wazo_confd import bus, sysconfd


class ExtensionNotifier:
    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, extension):
        self.send_sysconfd_handlers(['dialplan reload'])
        event = ExtensionCreatedEvent(
            extension.id, extension.exten, extension.context, extension.tenant_uuid
        )
        self.bus.send_bus_event(event)

    def edited(self, extension, updated_fields):
        if updated_fields is None or updated_fields:
            self.send_sysconfd_handlers(
                [
                    'dialplan reload',
                    'module reload res_pjsip.so',
                    'module reload chan_sccp.so',
                    'module reload app_queue.so',
                ]
            )
        event = ExtensionEditedEvent(
            extension.id, extension.exten, extension.context, extension.tenant_uuid
        )
        self.bus.send_bus_event(event)

    def deleted(self, extension):
        self.send_sysconfd_handlers(['dialplan reload'])
        event = ExtensionDeletedEvent(
            extension.id, extension.exten, extension.context, extension.tenant_uuid
        )
        self.bus.send_bus_event(event)


def build_notifier():
    return ExtensionNotifier(sysconfd, bus)
