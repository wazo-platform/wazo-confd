# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random

from . import confd


def generate_agent(**parameters):
    parameters.setdefault('number', generate_number())
    return add_agent(**parameters)


def add_agent(**parameters):
    response = confd.agents.post(parameters)
    return response.item


def delete_agent(agent_id, check=False):
    response = confd.agents(agent_id).delete()
    if check:
        response.assert_ok()


def generate_number():
    response = confd.agents.get()
    numbers = set(d['number'] for d in response.items)
    return _random_number(numbers)


def _random_number(numbers):
    number = ''.join(random.choice('0123456789') for i in range(4))
    if number in numbers:
        return _random_number(numbers)
    return number
