# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def add_iax(**params):
    response = confd.endpoints.iax.post(params)
    return response.item


def delete_iax(iax_id, check=False):
    response = confd.endpoints.iax(iax_id).delete()
    if check:
        response.assert_ok()


def generate_iax(**params):
    return add_iax(**params)
