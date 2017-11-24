# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def generate_register_sip(**params):
    params.setdefault('sip_username', 'sip-username-generated')
    params.setdefault('remote_host', 'remote-host-generated')
    return add_register_sip(**params)


def add_register_sip(**params):
    response = confd.registers.sip.post(params)
    return response.item


def delete_register_sip(register_sip_id, check=False):
    response = confd.registers.sip(register_sip_id).delete()
    if check:
        response.assert_ok()
