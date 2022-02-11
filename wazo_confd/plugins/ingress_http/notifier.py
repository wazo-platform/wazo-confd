# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
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
        headers = self._build_headers(ingress_http)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, ingress_http):
        serialized = IngressHTTPSchema().dump(ingress_http)
        event = EditIngressHTTPEvent(serialized)
        headers = self._build_headers(ingress_http)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, ingress_http):
        serialized = IngressHTTPSchema().dump(ingress_http)
        event = DeleteIngressHTTPEvent(serialized)
        headers = self._build_headers(ingress_http)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, ingress_http):
        return {'tenant_uuid': str(ingress_http.tenant_uuid)}


def build_notifier():
    return IngressHTTPNotifier(bus)
