# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd
from .. import config


def add_line(wazo_tenant=None, **params):
    response = confd.lines.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_line(line_id, check=False):
    response = confd.lines(line_id).delete()
    if check:
        response.assert_ok()


def generate_line(**params):
    params.setdefault('context', config.CONTEXT)
    return add_line(**params)
