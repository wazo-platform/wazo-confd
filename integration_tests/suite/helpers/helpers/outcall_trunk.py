# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(outcall_id, trunk_ids, check=True):
    trunks = [{'id': trunk_id} for trunk_id in trunk_ids]
    response = confd.outcalls(outcall_id).trunks.put(trunks=trunks)
    if check:
        response.assert_ok()


def dissociate(outcall_id, check=True):
    response = confd.outcalls(outcall_id).trunks.put(trunks=[])
    if check:
        response.assert_ok()
