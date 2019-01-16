# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def generate_schedule(**parameters):
    parameters.setdefault('closed_destination', {'type': 'none'})
    return add_schedule(**parameters)


def add_schedule(wazo_tenant=None, **parameters):
    response = confd.schedules.post(parameters, wazo_tenant=wazo_tenant)
    return response.item


def delete_schedule(schedule_id, check=False):
    response = confd.schedules(schedule_id).delete()
    if check:
        response.assert_ok()
