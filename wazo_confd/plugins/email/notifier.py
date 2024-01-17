# Copyright 2021-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.email.event import EmailConfigUpdatedEvent


class EmailConfigNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def edited(self):
        event = EmailConfigUpdatedEvent()
        self.bus.queue_event(event)
        self.sysconfd.commonconf_generate()
        self.sysconfd.commonconf_apply()
