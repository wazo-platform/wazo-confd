# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd
from ..config import CONTEXT


def generate_outcall(**parameters):
    parameters.setdefault('label', generate_label())
    parameters.setdefault('context', CONTEXT)
    return add_outcall(**parameters)


def add_outcall(wazo_tenant=None, **parameters):
    response = confd.outcalls.post(parameters, wazo_tenant=wazo_tenant)
    return response.item


def delete_outcall(outcall_id, check=False, **params):
    response = confd.outcalls(outcall_id).delete()
    if check:
        response.assert_ok()


def generate_label():
    response = confd.outcalls.get()
    labels = set(d['label'] for d in response.items)
    return _random_label(labels)


def _random_label(labels):
    label = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    while label in labels:
        label = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    return label
