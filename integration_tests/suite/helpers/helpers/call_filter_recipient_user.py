# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(call_filter_id, user_uuids, check=True):
    users = [{'uuid': user_uuid} for user_uuid in user_uuids]
    response = confd.callfilters(call_filter_id).recipients.users.put(users=users)
    if check:
        response.assert_ok()


def dissociate(call_filter_id, check=True):
    response = confd.callfilters(call_filter_id).recipients.users.put(users=[])
    if check:
        response.assert_ok()
