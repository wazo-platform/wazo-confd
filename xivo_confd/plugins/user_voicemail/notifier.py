# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.user_voicemail import event
from xivo_confd.helpers import sysconfd_connector
from xivo_confd.helpers import bus_manager


def associated(user, voicemail):
    sysconf_command_association_updated(user)
    bus_event_associated(user, voicemail)


def dissociated(user, voicemail):
    sysconf_command_association_updated(user)
    bus_event_dissociated(user, voicemail)


def sysconf_command_association_updated(user):
    command = {
        'ipbx': ['sip reload', 'module reload chan_sccp.so'],
        'agentbus': [],
        'ctibus': _generate_ctibus_commands(user)
    }
    sysconfd_connector.exec_request_handlers(command)


def _generate_ctibus_commands(user):
    ctibus = ['xivo[user,edit,%d]' % user.id]

    for line in user.lines:
        ctibus.append('xivo[phone,edit,%d]' % line.id)

    return ctibus


def bus_event_associated(user, voicemail):
    bus_event = event.UserVoicemailAssociatedEvent(user.uuid, voicemail.id)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)


def bus_event_dissociated(user, voicemail):
    bus_event = event.UserVoicemailDissociatedEvent(user.uuid, voicemail.id)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)
