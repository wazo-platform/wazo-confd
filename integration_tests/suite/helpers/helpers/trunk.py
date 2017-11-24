# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def generate_trunk(**params):
    return add_trunk(**params)


def add_trunk(**params):
    response = confd.trunks.post(params)
    return response.item


def delete_trunk(trunk_id, check=False):
    response = confd.trunks(trunk_id).delete()
    if check:
        response.assert_ok()
