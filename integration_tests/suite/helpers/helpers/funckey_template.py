# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def generate_funckey_template(**params):
    return add_funckey_template(**params)


def add_funckey_template(**params):
    response = confd.funckeys.templates.post(params)
    return response.item


def delete_funckey_template(funckey_template_id, check=False):
    response = confd.funckeys.templates(funckey_template_id).delete()
    if check:
        response.assert_ok()
