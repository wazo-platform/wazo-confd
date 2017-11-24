# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(outcall_id, schedule_id, check=True):
    response = confd.outcalls(outcall_id).schedules(schedule_id).put()
    if check:
        response.assert_ok()


def dissociate(outcall_id, schedule_id, check=True):
    response = confd.outcalls(outcall_id).schedules(schedule_id).delete()
    if check:
        response.assert_ok()
