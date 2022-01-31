# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.outcall_trunk.event import OutcallTrunksAssociatedEvent

from wazo_confd import bus


class OutcallTrunkNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated_all_trunks(self, outcall, trunks):
        trunk_ids = [trunk.id for trunk in trunks]
        event = OutcallTrunksAssociatedEvent(outcall.id, trunk_ids)
        headers = self._build_headers(outcall)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, outcall):
        return {'tenant_uuid': str(outcall.tenant_uuid)}


def build_notifier():
    return OutcallTrunkNotifier(bus)
