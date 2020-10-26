# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd


def generate_external_app(**parameters):
    return add_external_app(**parameters)


def add_external_app(wazo_tenant=None, **parameters):
    name = parameters.pop('name', generate_name())
    response = confd.external.apps(name).post(parameters, wazo_tenant=wazo_tenant)
    return response.item


def delete_external_app(name, check=False):
    response = confd.external.apps(name).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.external.apps.get()
    names = set(d['name'] for d in response.items)
    return _random_name(names)


def _random_name(names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in names:
        return _random_name(names)
    return name
