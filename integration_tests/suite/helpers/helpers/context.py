# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd


def generate_context(**parameters):
    parameters.setdefault('label', generate_label())
    parameters.setdefault('user_ranges', [{'start': '1000', 'end': '1999'}])
    parameters.setdefault('group_ranges', [{'start': '2000', 'end': '2999'}])
    parameters.setdefault('queue_ranges', [{'start': '3000', 'end': '3999'}])
    parameters.setdefault('conference_rooms_ranges', [{'start': '4000', 'end': '4999'}])
    parameters.setdefault('incall_ranges', [{'start': '1000', 'end': '9999'}])
    return add_context(**parameters)


def add_context(wazo_tenant=None, **parameters):
    response = confd.contexts.post(parameters, wazo_tenant=wazo_tenant)
    return response.item


def delete_context(context_id, check=False, **parameters):
    response = confd.contexts(context_id).delete()
    if check:
        response.assert_ok()


def generate_label():
    response = confd.contexts.get()
    labels = {d['label'] for d in response.items}
    return _random_label(labels)


def _random_label(labels):
    label = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if label in labels:
        return _random_label(labels)
    return label
