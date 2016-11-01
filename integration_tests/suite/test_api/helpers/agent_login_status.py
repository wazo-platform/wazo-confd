# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from test_api import db


def generate_agent_login_status(**parameters):
    return add_agent_login_status(**parameters)


def add_agent_login_status(**parameters):
    with db.queries() as queries:
        agent_id = queries.insert_agent_login_status(**parameters)
    return {'agent_id': agent_id,
            'id': agent_id}


def delete_agent_login_status(agent_id, check=False):
    with db.queries() as queries:
        queries.delete_agent_login_status(agent_id)
