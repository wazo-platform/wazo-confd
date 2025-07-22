# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd


def generate_call_filter(**params):
    label = generate_label()
    params.setdefault('label', label)
    params.setdefault('source', 'all')
    params.setdefault('strategy', 'all')
    return add_call_filter(**params)


def add_call_filter(wazo_tenant=None, **params):
    response = confd.callfilters.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_call_filter(call_filter_id, check=False, **kwargs):
    response = confd.callfilters(call_filter_id).delete()
    if check:
        response.assert_ok()


def generate_label():
    response = confd.callfilters.get()
    labels = set(d['label'] for d in response.items)
    return _random_label(labels)


def _random_label(labels):
    label = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    while label in labels:
        label = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    return label
