# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import confd


def add_custom(**params):
    response = confd.endpoints.custom.post(params)
    return response.item


def delete_custom(custom_id, check=False):
    response = confd.endpoints.custom(custom_id).delete()
    if check:
        response.assert_ok()


def generate_custom(**params):
    name = "".join(random.choice(string.lowercase) for _ in range(8))
    params.setdefault('interface', 'custom/{}'.format(name))
    return add_custom(**params)
