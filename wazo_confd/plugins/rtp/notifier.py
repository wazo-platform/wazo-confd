# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.rtp.event import (
    RTPGeneralEditedEvent,
    RTPIceHostCandidatesEditedEvent,
)

from wazo_confd import bus, sysconfd


class RTPConfigurationNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, section_name, rtp):
        if section_name == 'general':
            event = RTPGeneralEditedEvent()
            self.bus.queue_event(event)
        elif section_name == 'ice_host_candidates':
            event = RTPIceHostCandidatesEditedEvent()
            self.bus.queue_event(event)

        self.send_sysconfd_handlers(['module reload res_rtp_asterisk.so'])


def build_notifier():
    return RTPConfigurationNotifier(bus, sysconfd)
