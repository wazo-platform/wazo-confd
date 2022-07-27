# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
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
        handlers = {'ipbx': ipbx_commands}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, voicemail):
        self._send_sysconfd_handlers(['voicemail reload'])
        event = CreateVoicemailEvent(voicemail.id)
        headers = self._build_headers(voicemail)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, voicemail):
        self._send_sysconfd_handlers(
            [
                'voicemail reload',
                'module reload res_pjsip.so',
                'module reload chan_sccp.so',
            ]
        )
        event = EditVoicemailEvent(voicemail.id)
        headers = self._build_headers(voicemail)
        self.bus.send_bus_event(event, headers=headers)
        for user in voicemail.users:
            event = EditUserVoicemailEvent(user.uuid, voicemail.id)
            self.bus.send_bus_event(event, headers=headers)

    def deleted(self, voicemail):
        self._send_sysconfd_handlers(['voicemail reload'])
        event = DeleteVoicemailEvent(voicemail.id)
        headers = self._build_headers(voicemail)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, voicemail):
        return {'tenant_uuid': str(voicemail.tenant_uuid)}


def build_notifier():
    return VoicemailNotifier(bus, sysconfd)
