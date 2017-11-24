# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import confd


def generate_context(**parameters):
    parameters.setdefault('name', generate_name())
    parameters.setdefault('user_ranges', [{'start': '1000', 'end': '1999'}])
    parameters.setdefault('group_ranges', [{'start': '2000', 'end': '2999'}])
    parameters.setdefault('queue_ranges', [{'start': '3000', 'end': '3999'}])
    parameters.setdefault('conference_rooms_ranges', [{'start': '4000', 'end': '4999'}])
    parameters.setdefault('incall_ranges', [{'start': '1000', 'end': '9999'}])
    return add_context(**parameters)


def add_context(**parameters):
    response = confd.contexts.post(parameters)
    return response.item


def delete_context(context_id, check=False):
    response = confd.contexts(context_id).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.contexts.get()
    names = set(d['name'] for d in response.items)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
