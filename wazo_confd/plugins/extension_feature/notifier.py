# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.extension_feature.event import ExtensionFeatureEditedEvent

from wazo_confd import bus, sysconfd


class ExtensionFeatureNotifier:
    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, extension, updated_fields):
        event = ExtensionFeatureEditedEvent(extension.id)
        self.bus.queue_event(event)
        if updated_fields:
            self.send_sysconfd_handlers(['dialplan reload'])


def build_notifier():
    return ExtensionFeatureNotifier(sysconfd, bus)
