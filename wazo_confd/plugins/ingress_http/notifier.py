# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.ingress_http.event import (
    CreateIngressHTTPEvent,
    DeleteIngressHTTPEvent,
    EditIngressHTTPEvent,
)

from wazo_confd import bus

from .schema import IngressHTTPSchema


class IngressHTTPNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, ingress_http):
        serialized = IngressHTTPSchema().dump(ingress_http)
        event = CreateIngressHTTPEvent(serialized)
        self.bus.send_bus_event(event)

    def edited(self, ingress_http):
        serialized = IngressHTTPSchema().dump(ingress_http)
        event = EditIngressHTTPEvent(serialized)
        self.bus.send_bus_event(event)

    def deleted(self, ingress_http):
        serialized = IngressHTTPSchema().dump(ingress_http)
        event = DeleteIngressHTTPEvent(serialized)
        self.bus.send_bus_event(event)


def build_notifier():
    return IngressHTTPNotifier(bus)
