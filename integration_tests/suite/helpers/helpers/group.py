# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import confd


def generate_group(**parameters):
    parameters.setdefault('name', generate_name())
    return add_group(**parameters)


def add_group(**parameters):
    response = confd.groups.post(parameters)
    return response.item


def delete_group(group_id, check=False):
    response = confd.groups(group_id).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.groups.get()
    names = set(d['name'] for d in response.items)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
