# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd
from .. import config


def add_line(**params):
    response = confd.lines_sip.post(params)
    return response.item


def delete_line(line_id, check=False):
    response = confd.lines_sip(line_id).delete()
    if check:
        response.assert_ok()


def generate_line(**params):
    params.setdefault('context', config.CONTEXT)
    params.setdefault('device_slot', 1)
    return add_line(**params)
