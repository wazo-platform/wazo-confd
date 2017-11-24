# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import random
import string

from . import confd


def generate_paging(**parameters):
    parameters.setdefault('number', _generate_number())
    return add_paging(**parameters)


def _generate_number():
    response = confd.pagings.get()
    numbers = set(d['number'] for d in response.items)
    return _random_number(numbers)


def _random_number(numbers):
    number = ''.join(random.choice(string.digits) for _ in range(3))
    if number in numbers:
        return _random_number(numbers)
    return number


def add_paging(**parameters):
    response = confd.pagings.post(parameters)
    return response.item


def delete_paging(paging_id, check=False):
    response = confd.pagings(paging_id).delete()
    if check:
        response.assert_ok()
