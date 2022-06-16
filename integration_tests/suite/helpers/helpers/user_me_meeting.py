# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def add(confd_client, wazo_tenant=None, **params):
    response = confd_client.users.me.meetings.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete(uuid, check=False, **params):
    response = confd.meetings(uuid).delete()
    if check:
        response.assert_ok()


def generate(confd_client, **params):
    params.setdefault('name', 'meeting')
    return add(confd_client, **params)
