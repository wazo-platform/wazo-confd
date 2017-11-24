# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import confd


def generate_moh(**parameters):
    parameters.setdefault('name', generate_name())
    parameters.setdefault('mode', 'files')
    return add_moh(**parameters)


def add_moh(**parameters):
    response = confd.moh.post(parameters)
    return response.item


def delete_moh(moh_uuid, check=False):
    response = confd.moh(moh_uuid).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.moh.get()
    forbidden_names = set(d['name'] for d in response.items)
    return _random_name(forbidden_names)


def _random_name(forbidden_names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in forbidden_names:
        return _random_name(forbidden_names)
    return name
