# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def add_sip(**params):
    response = confd.endpoints.sip.post(params)
    return response.item


def delete_sip(sip_id, check=False):
    response = confd.endpoints.sip(sip_id).delete()
    if check:
        response.assert_ok()


def generate_sip(**params):
    return add_sip(**params)
