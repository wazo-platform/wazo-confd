# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import random
import string

from test_api import config
from test_api import db
from test_api.helpers import extension

SWITCHBOARD_STAT_QUEUE_NAME = 'sw_stats'


def new_switchboard(name=None):
    with db.queries() as queries:
        queue_name = name or 'sw_' + ''.join(random.choice(string.ascii_letters) for _ in range(10))
        queue_number = extension.find_available_exten(config.CONTEXT)
        queue_id = queries.insert_queue(queue_name, queue_number)
        id = queries.insert_switchboard(queue_id)
    return {'id': str(id)}


def find_switchboard(name):
    with db.queries() as queries:
        return queries.find_queue(name)


def generate_switchboard():
    return new_switchboard()


def generate_switchboard_stat(time, end_type='abandoned', wait_time=1):
    switchboard = find_switchboard(name=SWITCHBOARD_STAT_QUEUE_NAME)
    if not switchboard:
        switchboard = new_switchboard(name=SWITCHBOARD_STAT_QUEUE_NAME)

    stat = {'time': time,
            'end_type': end_type,
            'wait_time': wait_time,
            'queue_id': switchboard['id']}
    with db.queries() as queries:
        stat['id'] = queries.insert_switchboard_stat(**stat)

    return stat


def delete_switchboard_stat(stat_id, check=False):
    with db.queries() as queries:
        queries.delete_switchboard_stat(stat_id)
