# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.user_cti_profile.event import UserCtiProfileEditedEvent
from xivo_confd import bus


class UserCtiProfileNotifier(object):

    def __init__(self, bus):
        self._bus = bus

    def edited(self, user):
        event = UserCtiProfileEditedEvent(user.id, user.cti_profile_id, user.cti_enabled)
        self._bus.send_bus_event(event)


def build_notifier():
    return UserCtiProfileNotifier(bus)
