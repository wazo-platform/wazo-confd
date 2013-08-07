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

from acceptance.helpers.config import get_config_value
from lettuce.registry import world
from lettuce.terrain import before, after
from xivo_dao.helpers import config, db_manager
from acceptance.features_1_1.steps.helpers.remote import create_gateway


@before.all
def modify_db_uri():
    hostname = get_config_value('xivo', 'hostname')

    db_uri = 'postgresql://asterisk:proformatique@%s:5432/asterisk' % hostname

    config.DB_URI = db_uri
    db_manager.reinit()


@before.all
def open_gateway():
    world.gateway = create_gateway()


@after.all
def close_gateway(total):
    if hasattr(world, 'gateway'):
        world.gateway.exit()
