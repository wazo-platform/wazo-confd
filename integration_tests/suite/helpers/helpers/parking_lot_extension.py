# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(parking_lot_id, extension_id, check=True):
    response = confd.parkinglots(parking_lot_id).extensions(extension_id).put()
    if check:
        response.assert_ok()


def dissociate(parking_lot_id, extension_id, check=True):
    response = confd.parkinglots(parking_lot_id).extensions(extension_id).delete()
    if check:
        response.assert_ok()
