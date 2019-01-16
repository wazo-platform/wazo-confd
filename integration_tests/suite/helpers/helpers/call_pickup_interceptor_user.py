# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(call_pickup_id, user_uuids, check=True):
    users = [{'uuid': user_uuid} for user_uuid in user_uuids]
    response = confd.callpickups(call_pickup_id).interceptors.users.put(users=users)
    if check:
        response.assert_ok()


def dissociate(call_pickup_id, check=True):
    response = confd.callpickups(call_pickup_id).interceptors.users.put(users=[])
    if check:
        response.assert_ok()
