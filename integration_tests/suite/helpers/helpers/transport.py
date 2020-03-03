# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def generate_transport(**parameters):
    parameters.setdefault('name', 'my-transport')
    parameters.setdefault('options', [])
    return add_transport(**parameters)


def add_transport(**parameters):
    response = confd.sip.transports.post(parameters)
    return response.item


def delete_transport(transport_uuid, check=False):
    response = confd.sip.transports(transport_uuid).delete()
    if check:
        response.assert_ok()
