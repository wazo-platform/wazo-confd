# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(group_id, extensions, check=True):
    response = confd.groups(group_id).members.extensions.put(extensions=extensions)
    if check:
        response.assert_ok()


def dissociate(group_id, check=True):
    response = confd.groups(group_id).members.extensions.put(extensions=[])
    if check:
        response.assert_ok()
