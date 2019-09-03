# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.moh.event import (
    CreateMohEvent,
    DeleteMohEvent,
    EditMohEvent,
)

from wazo_confd import bus, sysconfd
from .schema import MohSchema

MOH_FIELDS = [
    'uuid',
    'tenant_uuid',
    'name',
]


class MohNotifier:

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['moh reload'],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, moh):
        self.send_sysconfd_handlers()
        moh_serialized = MohSchema(only=MOH_FIELDS).dump(moh)
        event = CreateMohEvent(moh_serialized)
        self.bus.send_bus_event(event)

    def edited(self, moh):
        self.send_sysconfd_handlers()
        moh_serialized = MohSchema(only=MOH_FIELDS).dump(moh)
        event = EditMohEvent(moh_serialized)
        self.bus.send_bus_event(event)

    def deleted(self, moh):
        self.send_sysconfd_handlers()
        moh_serialized = MohSchema(only=MOH_FIELDS).dump(moh)
        event = DeleteMohEvent(moh_serialized)
        self.bus.send_bus_event(event)

    def files_changed(self, moh):
        self.send_sysconfd_handlers()


def build_notifier():
    return MohNotifier(bus, sysconfd)
