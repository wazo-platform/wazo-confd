# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import string
import random

from . import confd


def generate_entity(**params):
    params.setdefault('name', generate_name())
    return add_entity(**params)


def add_entity(**params):
    response = confd.entities.post(params)
    return response.item


def delete_entity(entity_id, check=False):
    response = confd.entities(entity_id).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.entities.get()
    names = set(d['name'] for d in response.items)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.lowercase) for i in range(10))
    while name in names:
        name = ''.join(random.choice(string.lowercase) for i in range(10))
    return name
