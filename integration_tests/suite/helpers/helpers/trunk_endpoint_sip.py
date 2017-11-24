# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(trunk_id, endpoint_id, check=True):
    response = confd.trunks(trunk_id).endpoints.sip(endpoint_id).put()
    if check:
        response.assert_ok()


def dissociate(trunk_id, endpoint_id, check=True):
    response = confd.trunks(trunk_id).endpoints.sip(endpoint_id).delete()
    if check:
        response.assert_ok()
