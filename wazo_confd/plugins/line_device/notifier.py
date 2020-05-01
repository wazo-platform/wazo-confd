# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd import bus, sysconfd
from wazo_confd.plugins.line.schema import LineSchema
from wazo_confd.plugins.device.schema import DeviceSchema

from xivo_bus.resources.line_device.event import (
    LineDeviceAssociatedEvent,
    LineDeviceDissociatedEvent,
)

LINE_FIELDS = [
    'id',
    'name',
    'endpoint_sip.uuid',
    'endpoint_sccp.id',
    'endpoint_custom.id',
]

DEVICE_FIELDS = ['id']


class LineDeviceNotifier:

    REQUEST_HANDLERS = {'ipbx': ['module reload chan_sccp.so'], 'agentbus': []}

    def __init__(self, bus, sysconfd):
        self._bus = bus
        self._sysconfd = sysconfd

    def associated(self, line, device):
        self._reload_sccp(line)

        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        device_serialized = DeviceSchema(only=DEVICE_FIELDS).dump(device)
        event = LineDeviceAssociatedEvent(
            line=line_serialized, device=device_serialized
        )
        self._bus.send_bus_event(event)

    def dissociated(self, line, device):
        self._reload_sccp(line)

        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        device_serialized = DeviceSchema(only=DEVICE_FIELDS).dump(device)
        event = LineDeviceDissociatedEvent(
            line=line_serialized, device=device_serialized
        )
        self._bus.send_bus_event(event)

    def _reload_sccp(self, line):
        if line.endpoint_sccp_id:
            self._sysconfd.exec_request_handlers(self.REQUEST_HANDLERS)


def build_notifier():
    return LineDeviceNotifier(bus, sysconfd)
