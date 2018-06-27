# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(queue_id, schedule_id, check=True):
    response = confd.queues(queue_id).schedules(schedule_id).put()
    if check:
        response.assert_ok()


def dissociate(queue_id, schedule_id, check=True):
    response = confd.queues(queue_id).schedules(schedule_id).delete()
    if check:
        response.assert_ok()
