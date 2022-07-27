# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.voicemail_zonemessages.event import (
    VoicemailZoneMessagesEditedEvent,
)

from wazo_confd import bus, sysconfd


class VoicemailZoneMessagesNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, voicemail_zonemessages):
        event = VoicemailZoneMessagesEditedEvent()
        self.bus.queue_event(event)
        self.send_sysconfd_handlers(['voicemail reload'])


def build_notifier():
    return VoicemailZoneMessagesNotifier(bus, sysconfd)
