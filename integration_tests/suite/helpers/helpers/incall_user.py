# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(incall_id, user_id, check=True):
    response = confd.incalls(incall_id).put(destination={'type': 'user',
                                                         'user_id': user_id})
    if check:
        response.assert_ok()


def dissociate(incall_id, extension_id, check=True):
    response = confd.incalls(incall_id).put(destination={'type': 'none'})
    if check:
        response.assert_ok()
