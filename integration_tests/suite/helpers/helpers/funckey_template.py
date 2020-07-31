# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def generate_funckey_template(**params):
    return add_funckey_template(**params)


def add_funckey_template(wazo_tenant=None, **params):
    response = confd.funckeys.templates.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_funckey_template(funckey_template_id, check=False):
    response = confd.funckeys.templates(funckey_template_id).delete()
    if check:
        response.assert_ok()
