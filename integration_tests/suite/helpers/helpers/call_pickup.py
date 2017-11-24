# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import db


def generate_call_pickup(**parameters):
    parameters.setdefault('name', _random_name())

    with db.queries() as queries:
        id = queries.insert_call_pickup(**parameters)
    return {'id': id}


def delete_call_pickup(call_pickup, check=False):
    with db.queries() as queries:
        queries.delete_call_pickup(call_pickup)


def _random_name():
    return ''.join(random.choice(string.lowercase) for i in range(10))
