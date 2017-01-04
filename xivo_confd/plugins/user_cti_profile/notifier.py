# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
