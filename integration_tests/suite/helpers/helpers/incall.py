# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def generate_incall(**params):
    params.setdefault('destination', {'type': 'none'})
    return add_incall(**params)


def add_incall(wazo_tenant=None, **params):
    response = confd.incalls.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_incall(incall_id, check=False):
    response = confd.incalls(incall_id).delete()
    if check:
        response.assert_ok()
