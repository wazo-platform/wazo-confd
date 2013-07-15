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
import xivo_ws

from acceptance.helpers.config import get_config_value
from lettuce.registry import world
from lettuce.terrain import before
from xivo_dao.helpers import config, db_manager


@before.all
def modify_db_uri():
    hostname = get_config_value('xivo', 'hostname')
    login = get_config_value('xivo_ws', 'login')
    password = get_config_value('xivo_ws', 'password')

    db_uri = 'postgresql://asterisk:proformatique@%s:5432/asterisk' % hostname

    config.DB_URI = db_uri
    db_manager.reinit()

    world.ws = xivo_ws.XivoServer(hostname, login, password)


@before.each_scenario
def reset_world(scenario):
    world.voicemailid = None
    world.userid = None
    world.number = None
    world.lineid = None
