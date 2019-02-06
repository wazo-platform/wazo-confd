# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd


def generate_sound(**parameters):
    parameters.setdefault('name', generate_name())
    return add_sound(**parameters)


def add_sound(wazo_tenant, **parameters):
    response = confd.sounds.post(parameters, wazo_tenant=wazo_tenant)
    return response.item


def delete_sound(sound_name, check=False):
    response = confd.sounds(sound_name).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.sounds.get()
    forbidden_names = set(d['name'] for d in response.items)
    return _random_name(forbidden_names)


def _random_name(forbidden_names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in forbidden_names:
        return _random_name(forbidden_names)
    return name
