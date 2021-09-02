# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd import bus


class Notifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, meeting):
        pass

    def edited(self, meeting):
        pass

    def deleted(self, meeting):
        pass


def build_notifier():
    return Notifier(bus)
