# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def generate_ingress_http(**parameters):
    parameters.setdefault('uri', 'https://test.example.com')
    return add_ingress_http(**parameters)


def delete_ingress_http(uuid, check=False, **parameters):
    response = confd.ingresses.http(uuid).delete()
    if check:
        response.assert_ok()


def add_ingress_http(wazo_tenant=None, **parameters):
    response = confd.ingresses.http.post(parameters, wazo_tenant=wazo_tenant)
    return response.item
