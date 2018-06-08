# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import confd


def generate_queue(**parameters):
    parameters.setdefault('name', generate_name())
    return add_queue(**parameters)


def add_queue(**parameters):
    response = confd.queues.post(parameters)
    return response.item


def delete_queue(queue_id, check=False):
    response = confd.queues(queue_id).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.queues.get()
    names = set(d['name'] for d in response.items)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
