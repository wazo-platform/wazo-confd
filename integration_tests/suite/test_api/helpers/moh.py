# -*- coding: UTF-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

import random
import string

from test_api import confd


def generate_moh(**parameters):
    parameters.setdefault('name', generate_name())
    parameters.setdefault('mode', 'files')
    return add_moh(**parameters)


def add_moh(**parameters):
    response = confd.moh.post(parameters)
    return response.item


def delete_moh(moh_uuid, check=False):
    response = confd.moh(moh_uuid).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.moh.get()
    forbidden_names = set(d['name'] for d in response.items)
    return _random_name(forbidden_names)


def _random_name(forbidden_names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in forbidden_names:
        return _random_name(forbidden_names)
    return name
