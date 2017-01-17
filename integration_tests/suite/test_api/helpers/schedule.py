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

from test_api import confd


def generate_schedule(**parameters):
    parameters.setdefault('closed_destination', {'type': 'none'})
    return add_schedule(**parameters)


def add_schedule(**parameters):
    response = confd.schedules.post(parameters)
    return response.item


def delete_schedule(schedule_id, check=False):
    response = confd.schedules(schedule_id).delete()
    if check:
        response.assert_ok()
