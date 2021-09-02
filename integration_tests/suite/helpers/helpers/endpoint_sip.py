# Copyright 2015-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def add_sip(wazo_tenant=None, **params):
    response = confd.endpoints.sip.post(params, wazo_tenant=wazo_tenant)
    return response.item


def add_sip_template(wazo_tenant=None, **params):
    response = confd.endpoints.sip.templates.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_sip(sip_uuid, check=False, **params):
    response = confd.endpoints.sip(sip_uuid).delete()
    if check:
        response.assert_ok()


def delete_sip_template(sip_template_uuid, check=False, **params):
    response = confd.endpoints.sip.templates(sip_template_uuid).delete()
    if check:
        response.assert_ok()


def generate_sip(**params):
    return add_sip(**params)


def generate_sip_template(**params):
    return add_sip_template(**params)
