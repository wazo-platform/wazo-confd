# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.user_voicemail.event import (
    UserVoicemailAssociatedEvent,
    UserVoicemailDissociatedEvent,
)

from wazo_confd import bus, sysconfd


class UserVoicemailNotifier:
    def __init__(self, bus, sysconfd):
        self._bus = bus
        self._sysconfd = sysconfd

    def _send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['module reload res_pjsip.so', 'module reload chan_sccp.so']
        }
        self._sysconfd.exec_request_handlers(handlers)

    def associated(self, user, voicemail):
        self._send_sysconfd_handlers()
        event = UserVoicemailAssociatedEvent(voicemail.id, user.tenant_uuid, user.uuid)
        self._bus.queue_event(event)

    def dissociated(self, user, voicemail):
        self._send_sysconfd_handlers()
        event = UserVoicemailDissociatedEvent(voicemail.id, user.tenant_uuid, user.uuid)
        self._bus.queue_event(event)


def build_notifier():
    return UserVoicemailNotifier(bus, sysconfd)
