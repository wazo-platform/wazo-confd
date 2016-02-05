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


def new_call_permission(name):
    with db.queries() as queries:
        id = queries.insert_call_permission(name)
    return {'id': id,
            'name': name}


def generate_call_permission(name=None):
    name = name or 'cp_' + ''.join(random.choice(string.ascii_letters) for _ in range(10))
    return new_call_permission(name)


def delete_call_permission(permission_id, check=False):
    with db.queries() as queries:
        queries.delete_call_permission(permission_id)
