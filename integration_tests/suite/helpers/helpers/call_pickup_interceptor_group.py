# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(call_pickup_id, group_ids, check=True):
    groups = [{'id': group_id} for group_id in group_ids]
    response = confd.callpickups(call_pickup_id).interceptors.groups.put(groups=groups)
    if check:
        response.assert_ok()


def dissociate(call_pickup_id, check=True):
    response = confd.callpickups(call_pickup_id).interceptors.groups.put(groups=[])
    if check:
        response.assert_ok()
