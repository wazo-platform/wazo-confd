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

from test_api import db


def generate_call_log(date, date_answer, date_end, source_name, source_exten, destination_exten, user_field=''):
    call_log = {'date': date,
                'date_answer': date_answer,
                'date_end': date_end,
                'source_name': source_name,
                'source_exten': source_exten,
                'destination_exten': destination_exten,
                'user_field': user_field}

    with db.queries() as queries:
        call_log['id'] = queries.insert_call_log(**call_log)

    return call_log


def delete_call_log(call_log_id, check=False):
    with db.queries() as queries:
        queries.delete_call_log(call_log_id)
