# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.features.event import (
    FeaturesApplicationmapEditedEvent,
    FeaturesFeaturemapEditedEvent,
    FeaturesGeneralEditedEvent,
)

from wazo_confd import bus, sysconfd


class FeaturesConfigurationNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, section_name, features):
        if section_name == 'applicationmap':
            event = FeaturesApplicationmapEditedEvent()
            self.bus.queue_event(event)
        elif section_name == 'featuremap':
            event = FeaturesFeaturemapEditedEvent()
            self.bus.queue_event(event)
        elif section_name == 'general':
            event = FeaturesGeneralEditedEvent()
            self.bus.queue_event(event)

        self.send_sysconfd_handlers(['module reload features'])


def build_notifier():
    return FeaturesConfigurationNotifier(bus, sysconfd)
