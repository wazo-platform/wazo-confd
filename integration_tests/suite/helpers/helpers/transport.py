# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd


def generate_transport(**parameters):
    parameters.setdefault('name', generate_name())
    parameters.setdefault('options', [])
    return add_transport(**parameters)


def add_transport(**parameters):
    response = confd.sip.transports.post(parameters)
    return response.item


def delete_transport(transport_uuid, check=False, **parameters):
    response = confd.sip.transports(transport_uuid).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.sip.transports.get()
    names = {d['name'] for d in response.items}
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
