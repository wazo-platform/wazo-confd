# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def generate_incall(**params):
    params.setdefault('destination', {'type': 'none'})
    return add_incall(**params)


def add_incall(**params):
    response = confd.incalls.post(params)
    return response.item


def delete_incall(incall_id, check=False):
    response = confd.incalls(incall_id).delete()
    if check:
        response.assert_ok()
