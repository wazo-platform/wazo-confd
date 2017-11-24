# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from . import confd


def add_sccp(**params):
    response = confd.endpoints.sccp.post(params)
    return response.item


def delete_sccp(sccp_id, check=False):
    response = confd.endpoints.sccp(sccp_id).delete()
    if check:
        response.assert_ok()


def generate_sccp(**params):
    return add_sccp(**params)
