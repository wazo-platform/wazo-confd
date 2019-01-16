# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def add_iax(wazo_tenant=None, **params):
    response = confd.endpoints.iax.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_iax(iax_id, check=False):
    response = confd.endpoints.iax(iax_id).delete()
    if check:
        response.assert_ok()


def generate_iax(**params):
    return add_iax(**params)
