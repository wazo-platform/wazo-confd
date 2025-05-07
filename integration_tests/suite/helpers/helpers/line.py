# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .. import config
from . import confd


def add_line(wazo_tenant=None, **params):
    response = confd.lines.post(params, wazo_tenant=wazo_tenant)
    return response.item


def delete_line(line_id, check=False, **params):
    response = confd.lines(line_id).delete()
    if check:
        response.assert_ok()


def generate_line(**params):
    params.setdefault('context', config.CONTEXT)
    return add_line(**params)
