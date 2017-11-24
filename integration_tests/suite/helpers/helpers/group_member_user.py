# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(group_id, user_uuids, check=True):
    users = [{'uuid': user_uuid} for user_uuid in user_uuids]
    response = confd.groups(group_id).members.users.put(users=users)
    if check:
        response.assert_ok()


def dissociate(group_id, check=True):
    response = confd.groups(group_id).members.users.put(users=[])
    if check:
        response.assert_ok()
