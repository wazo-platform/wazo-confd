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

from xivo_bus.resources.configuration import event
from xivo_confd.helpers import bus_manager, sysconfd_connector


def live_reload_status_changed(data):
    bus_event = event.LiveReloadEditedEvent(data['enabled'])
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)
    if data['enabled']:
        _send_sysconfd_command()


def _send_sysconfd_command():
    command_dict = {
        'ctibus': ['xivo[cticonfig,update]'],
        'dird': [],
        'ipbx': [],
        'agentbus': [],
    }
    sysconfd_connector.exec_request_handlers(command_dict)
