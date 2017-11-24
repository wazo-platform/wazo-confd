# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import string
import random

from . import confd


def generate_call_permission(**params):
    name = generate_name()
    params.setdefault('name', name)
    return add_call_permission(**params)


def add_call_permission(**params):
    response = confd.callpermissions.post(params)
    return response.item


def delete_call_permission(call_permission_id, check=False):
    response = confd.callpermissions(call_permission_id).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.callpermissions.get()
    names = set(d['name'] for d in response.items)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.lowercase) for i in range(10))
    while name in names:
        name = ''.join(random.choice(string.lowercase) for i in range(10))
    return name
