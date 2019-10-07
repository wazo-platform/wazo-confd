# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.rtp.event import (
    EditRTPGeneralEvent,
    EditRTPIceHostCandidatesEvent,
)

from wazo_confd import bus, sysconfd


class RTPConfigurationNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, section_name, rtp):
        if section_name == 'general':
            event = EditRTPGeneralEvent()
            self.bus.send_bus_event(event)
        elif section_name == 'ice_host_candidates':
            event = EditRTPIceHostCandidatesEvent()
            self.bus.send_bus_event(event)

        self.send_sysconfd_handlers(['module reload res_rtp_asterisk.so'])


def build_notifier():
    return RTPConfigurationNotifier(bus, sysconfd)
