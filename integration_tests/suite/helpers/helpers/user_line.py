# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(user_id, line_id, check=True):
    response = confd.users(user_id).lines.post(line_id=line_id)
    if check:
        response.assert_ok()


def dissociate(user_id, line_id, check=True):
    response = confd.users(user_id).lines(line_id).delete()
    if check:
        response.assert_ok()
