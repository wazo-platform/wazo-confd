# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def add_sccp(wazo_tenant=None, **params):
    response = confd.endpoints.sccp.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_sccp(sccp_id, check=False):
    response = confd.endpoints.sccp(sccp_id).delete()
    if check:
        response.assert_ok()


def generate_sccp(**params):
    return add_sccp(**params)
