# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.voicemail.event import (
    CreateVoicemailEvent,
    DeleteVoicemailEvent,
    EditUserVoicemailEvent,
    EditVoicemailEvent,
)

from wazo_confd import bus, sysconfd


class VoicemailNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def _send_sysconfd_handlers(self, ipbx_commands):
        handlers = {'ipbx': ipbx_commands, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, voicemail):
        self._send_sysconfd_handlers(['voicemail reload'])
        event = CreateVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event)

    def edited(self, voicemail):
        self._send_sysconfd_handlers(
            [
                'voicemail reload',
                'module reload res_pjsip.so',
                'module reload chan_sccp.so',
            ]
        )
        event = EditVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event)
        for user in voicemail.users:
            event = EditUserVoicemailEvent(user.uuid, voicemail.id)
            self.bus.send_bus_event(event)

    def deleted(self, voicemail):
        self._send_sysconfd_handlers(['voicemail reload'])
        event = DeleteVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return VoicemailNotifier(bus, sysconfd)
