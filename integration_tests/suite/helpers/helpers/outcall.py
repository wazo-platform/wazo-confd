# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import confd
from ..config import CONTEXT


def generate_outcall(**parameters):
    parameters.setdefault('name', generate_name())
    parameters.setdefault('context', CONTEXT)
    return add_outcall(**parameters)


def add_outcall(**parameters):
    response = confd.outcalls.post(parameters)
    return response.item


def delete_outcall(outcall_id, check=False):
    response = confd.outcalls(outcall_id).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.outcalls.get()
    names = set(d['name'] for d in response.items)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
