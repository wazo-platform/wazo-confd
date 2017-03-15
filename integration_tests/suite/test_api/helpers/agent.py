# -*- coding: UTF-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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

from test_api import db


def generate_agent(**parameters):
    parameters.setdefault('number', generate_number())
    return add_agent(**parameters)


def add_agent(**parameters):
    with db.queries() as queries:
        id = queries.insert_agent(**parameters)
    return {'id': id,
            'number': parameters.get('number')}


def delete_agent(agent_id, check=False):
    with db.queries() as queries:
        queries.delete_agent(agent_id)


def generate_number():
    with db.queries() as queries:
        response = queries.get_agent()
    numbers = set(d['number'] for d in response)
    return _random_number(numbers)


def _random_number(numbers):
    number = ''.join(random.choice('0123456789') for i in range(4))
    while number in numbers:
        number = ''.join(random.choice('0123456789') for i in range(4))
    return number
