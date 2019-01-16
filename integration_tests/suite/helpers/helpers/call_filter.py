# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import string
import random

from . import confd


def generate_call_filter(**params):
    name = generate_name()
    params.setdefault('name', name)
    params.setdefault('source', 'all')
    params.setdefault('strategy', 'all')
    return add_call_filter(**params)


def add_call_filter(wazo_tenant=None, **params):
    response = confd.callfilters.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_call_filter(call_filter_id, check=False):
    response = confd.callfilters(call_filter_id).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.callfilters.get()
    names = set(d['name'] for d in response.items)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    while name in names:
        name = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    return name
