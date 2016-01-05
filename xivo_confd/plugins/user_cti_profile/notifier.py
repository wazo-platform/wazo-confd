# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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


def edited(user_cti_profile):
    bus_event = event.UserCtiProfileEditedEvent(user_cti_profile.user_id,
                                                user_cti_profile.cti_profile_id,
                                                user_cti_profile.enabled)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)
    _send_sysconfd_command(user_cti_profile)


def _send_sysconfd_command(user_cti_profile):
    command_dict = {
        'ctibus': _generate_cti_commands(user_cti_profile),
        'dird': [],
        'ipbx': [],
        'agentbus': [],
    }
    sysconfd_connector.exec_request_handlers(command_dict)


def _generate_cti_commands(user_cti_profile):
    return ['xivo[user,edit,%d]' % user_cti_profile.user_id]
