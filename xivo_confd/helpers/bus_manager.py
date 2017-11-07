# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.application import get_bus_publisher


def send_bus_event(event, routing_key):
    bus = get_bus_publisher()
    bus.send_bus_event(event, routing_key)
