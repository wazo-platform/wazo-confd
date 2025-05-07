# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from ..config import CONTEXT
from . import confd


def generate_outcall(**parameters):
    parameters.setdefault('name', generate_name())
    parameters.setdefault('context', CONTEXT)
    return add_outcall(**parameters)


def add_outcall(wazo_tenant=None, **parameters):
    response = confd.outcalls.post(parameters, wazo_tenant=wazo_tenant)
    return response.item


def delete_outcall(outcall_id, check=False, **params):
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
