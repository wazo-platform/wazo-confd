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

import random
import string

from test_api import confd


def generate_context(**parameters):
    parameters.setdefault('name', generate_name())
    parameters.setdefault('user_ranges', [{'start': '1000', 'end': '1999'}])
    parameters.setdefault('group_ranges', [{'start': '2000', 'end': '2999'}])
    parameters.setdefault('queue_ranges', [{'start': '3000', 'end': '3999'}])
    parameters.setdefault('conference_rooms_ranges', [{'start': '4000', 'end': '4999'}])
    parameters.setdefault('incall_ranges', [{'start': '1000', 'end': '9999'}])
    return add_context(**parameters)


def add_context(**parameters):
    response = confd.contexts.post(parameters)
    return response.item


def delete_context(context_id, check=False):
    response = confd.contexts(context_id).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.contexts.get()
    names = set(d['name'] for d in response.items)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
