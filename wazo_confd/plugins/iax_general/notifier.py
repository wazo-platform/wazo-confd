# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.iax_general.event import IAXGeneralEditedEvent

from wazo_confd import bus, sysconfd


class IAXGeneralNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, iax_general):
        event = IAXGeneralEditedEvent()
        self.bus.queue_event(event)
        self.send_sysconfd_handlers(['iax2 reload'])


def build_notifier():
    return IAXGeneralNotifier(bus, sysconfd)
