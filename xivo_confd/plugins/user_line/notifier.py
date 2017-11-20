# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.user_line import event
from xivo_confd.helpers import sysconfd_connector
from xivo_confd.helpers import bus_manager


def associated(user_line):
    sysconf_command_association_updated(user_line)
    bus_event_associated(user_line)


def dissociated(user_line):
    sysconf_command_association_updated(user_line)
    bus_event_dissociated(user_line)


def sysconf_command_association_updated(user_line):
    command = {
        'ipbx': ['dialplan reload', 'sip reload'],
        'agentbus': [],
        'ctibus': [],
    }
    sysconfd_connector.exec_request_handlers(command)


def bus_event_associated(user_line):
    bus_event = event.UserLineAssociatedEvent(user_line.user_id,
                                              user_line.line_id,
                                              user_line.main_user,
                                              user_line.main_line)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)


def bus_event_dissociated(user_line):
    bus_event = event.UserLineDissociatedEvent(user_line.user_id,
                                               user_line.line_id,
                                               user_line.main_user,
                                               user_line.main_line)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)
