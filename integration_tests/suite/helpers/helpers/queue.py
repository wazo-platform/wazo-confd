# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import db


def generate_queue(**parameters):
    parameters.setdefault('name', generate_name())
    return add_queue(**parameters)


def add_queue(**parameters):
    with db.queries() as queries:
        id_ = queries.insert_queue_only(**parameters)
    parameters['id'] = id_
    return parameters


def delete_queue(queue_id, check=False):
    with db.queries() as queries:
        queries.delete_queue(queue_id)


def generate_name():
    with db.queries() as queries:
        response = queries.get_queues()
    names = set(d['name'] for d in response)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
