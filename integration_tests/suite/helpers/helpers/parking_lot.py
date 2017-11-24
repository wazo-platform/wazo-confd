# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def generate_parking_lot(**parameters):
    parameters.setdefault('slots_start', '701')
    parameters.setdefault('slots_end', '750')
    return add_parking_lot(**parameters)


def add_parking_lot(**parameters):
    response = confd.parkinglots.post(parameters)
    return response.item


def delete_parking_lot(parking_lot_id, check=False):
    response = confd.parkinglots(parking_lot_id).delete()
    if check:
        response.assert_ok()
