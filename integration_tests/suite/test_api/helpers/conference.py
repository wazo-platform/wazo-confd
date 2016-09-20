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

from test_api import db


def generate_conference(**parameters):
    parameters.setdefault('name', generate_name())
    return add_conference(**parameters)


def add_conference(**parameters):
    with db.queries() as queries:
        id_ = queries.insert_conference_only(**parameters)
    parameters['id'] = id_
    return parameters


def delete_conference(conference_id, check=False):
    with db.queries() as queries:
        queries.delete_conference(conference_id)


def generate_name():
    with db.queries() as queries:
        response = queries.get_conferences()
    names = set(d['name'] for d in response)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
