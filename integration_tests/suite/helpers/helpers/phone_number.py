# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd


def generate_phone_number(**parameters):
    parameters.setdefault('number', _random_number(10))
    return add_phone_number(**parameters)


def generate_phone_number_range(**parameters):
    parameters.setdefault('start_number', _random_number(10))
    parameters.setdefault(
        'end_number', subsequent_phone_number(parameters['start_number'], 10)
    )
    response = confd.phone_numbers.ranges.post(**parameters)
    return response.item


def delete_phone_number(phone_number_uuid, check=False, **parameters):
    response = confd.phone_numbers(phone_number_uuid).delete()
    if check:
        response.assert_ok()


def add_phone_number(wazo_tenant=None, **parameters):
    response = confd.phone_numbers.post(parameters, wazo_tenant=wazo_tenant)
    return response.item


def _random_number(length):
    number = ''.join(random.choice(string.digits) for _ in range(length))
    return f'+{number}'


def subsequent_phone_number(start_number, skip_count=1):
    number_as_int = int(start_number.replace('+', ''))
    subsequent_number = number_as_int + skip_count
    return (
        f'+{subsequent_number}'
        if start_number.startswith('+')
        else str(subsequent_number)
    )
