# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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

import execnet
from lettuce import world

from acceptance.helpers.config import get_config_value


def create_gateway():
    host = get_config_value('xivo', 'hostname')
    username = 'root'
    gw = execnet.makegateway('ssh=%s@%s' % (username, host))
    return gw


def remote_exec(func, **kwargs):
    gw = world.gateway
    channel = gw.remote_exec(func, **kwargs)
    channel.waitclose()
