# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(user_id, entity_id, check=True):
    response = confd.users(user_id).entities(entity_id).put()
    if check:
        response.assert_ok()
