# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd


def generate_phone_number(**parameters):
    parameters.setdefault('number', _random_number(10))
    return add_phone_number(**parameters)


def delete_phone_number(phone_number_uuid, check=False, **parameters):
    response = confd.phone_numbers(phone_number_uuid).delete()
    if check:
        response.assert_ok()


def add_phone_number(wazo_tenant=None, **parameters):
    response = confd.phone_numbers.post(parameters, wazo_tenant=wazo_tenant)
    return response.item


def _random_number(length):
    number = number = ''.join(random.choice(string.digits) for _ in range(length))
    return f'+{number}'
