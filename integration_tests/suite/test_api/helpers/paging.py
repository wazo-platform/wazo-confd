# -*- coding: UTF-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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

from test_api import confd


def generate_paging(**parameters):
    parameters.setdefault('number', _generate_number())
    return add_paging(**parameters)


def _generate_number():
    response = confd.pagings.get()
    numbers = set(d['number'] for d in response.items)
    return _random_number(numbers)


def _random_number(numbers):
    number = ''.join(random.choice(string.digits) for _ in range(3))
    if number in numbers:
        return _random_number(numbers)
    return number


def add_paging(**parameters):
    response = confd.pagings.post(parameters)
    return response.item


def delete_paging(paging_id, check=False):
    response = confd.pagings(paging_id).delete()
    if check:
        response.assert_ok()
