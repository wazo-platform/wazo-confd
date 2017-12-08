# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.voicemail.event import (
    CreateVoicemailEvent,
    DeleteVoicemailEvent,
    EditUserVoicemailEvent,
    EditVoicemailEvent,
)


class VoicemailNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def _send_sysconfd_handlers(self, ctibus_command, ipbx_commands):
        handlers = {
            'ctibus': [ctibus_command],
            'ipbx': ipbx_commands,
            'agentbus': []
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, voicemail):
        self._send_sysconfd_handlers('xivo[voicemail,add,%s]' % voicemail.id,
                                     ['voicemail reload'])
        event = CreateVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event)

    def edited(self, voicemail):
        self._send_sysconfd_handlers('xivo[voicemail,edit,%s]' % voicemail.id,
                                     ['voicemail reload',
                                      'sip reload',
                                      'module reload chan_sccp.so'])
        event = EditVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event)
        for user in voicemail.users:
            event = EditUserVoicemailEvent(user.uuid, voicemail.id)
            self.bus.send_bus_event(event)

    def deleted(self, voicemail):
        self._send_sysconfd_handlers('xivo[voicemail,delete,%s]' % voicemail.id,
                                     ['voicemail reload'])
        event = DeleteVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return VoicemailNotifier(bus, sysconfd)
