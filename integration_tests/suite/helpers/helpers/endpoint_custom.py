# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd


def add_custom(wazo_tenant=None, **params):
    response = confd.endpoints.custom.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_custom(custom_id, check=False):
    response = confd.endpoints.custom(custom_id).delete()
    if check:
        response.assert_ok()


def generate_custom(**params):
    name = "".join(random.choice(string.ascii_lowercase) for _ in range(8))
    params.setdefault('interface', 'custom/{}'.format(name))
    return add_custom(**params)
