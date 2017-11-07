# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.user_cti_profile import event
from xivo_confd.helpers import bus_manager, sysconfd_connector


def edited(user):
    bus_event = event.UserCtiProfileEditedEvent(user.id,
                                                user.cti_profile_id,
                                                user.cti_enabled)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)
    _send_sysconfd_command(user)


def _send_sysconfd_command(user):
    command_dict = {
        'ctibus': _generate_cti_commands(user),
        'ipbx': [],
        'agentbus': [],
    }
    sysconfd_connector.exec_request_handlers(command_dict)


def _generate_cti_commands(user):
    return ['xivo[user,edit,%d]' % user.id]
