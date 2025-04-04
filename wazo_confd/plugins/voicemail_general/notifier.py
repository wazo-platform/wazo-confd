# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.voicemail_general.event import VoicemailGeneralEditedEvent

from wazo_confd import bus, sysconfd


class VoicemailGeneralNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, voicemail_general):
        event = VoicemailGeneralEditedEvent()
        self.bus.queue_event(event)
        self.send_sysconfd_handlers(['voicemail reload'])


def build_notifier():
    return VoicemailGeneralNotifier(bus, sysconfd)
