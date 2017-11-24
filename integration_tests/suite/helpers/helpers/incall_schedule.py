# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(incall_id, schedule_id, check=True):
    response = confd.incalls(incall_id).schedules(schedule_id).put()
    if check:
        response.assert_ok()


def dissociate(incall_id, schedule_id, check=True):
    response = confd.incalls(incall_id).schedules(schedule_id).delete()
    if check:
        response.assert_ok()
