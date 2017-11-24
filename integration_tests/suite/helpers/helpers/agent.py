# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random

from . import db


def generate_agent(**parameters):
    parameters.setdefault('number', generate_number())
    return add_agent(**parameters)


def add_agent(**parameters):
    with db.queries() as queries:
        id = queries.insert_agent(**parameters)
    return {'id': id,
            'number': parameters.get('number')}


def delete_agent(agent_id, check=False):
    with db.queries() as queries:
        queries.delete_agent(agent_id)


def generate_number():
    with db.queries() as queries:
        response = queries.get_agent()
    numbers = set(d['number'] for d in response)
    return _random_number(numbers)


def _random_number(numbers):
    number = ''.join(random.choice('0123456789') for i in range(4))
    while number in numbers:
        number = ''.join(random.choice('0123456789') for i in range(4))
    return number
