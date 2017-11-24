# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import db


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
