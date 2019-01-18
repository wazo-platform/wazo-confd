# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd


def generate_ivr(**parameters):
    parameters.setdefault('name', _random_name())
    parameters.setdefault('menu_sound', 'hello-world')
    return add_ivr(**parameters)


def add_ivr(wazo_tenant=None, **parameters):
    response = confd.ivr.post(parameters, wazo_tenant=wazo_tenant)
    return response.item


def delete_ivr(ivr_id, check=False):
    response = confd.ivr(ivr_id).delete()
    if check:
        response.assert_ok()


def _random_name():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
