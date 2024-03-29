# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def generate_trunk(**params):
    return add_trunk(**params)


def add_trunk(wazo_tenant=None, **params):
    response = confd.trunks.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_trunk(trunk_id, check=False, **params):
    response = confd.trunks(trunk_id).delete()
    if check:
        response.assert_ok()
