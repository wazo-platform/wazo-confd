# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import db


def associate(schedule_id, entity_id, check=True):
    with db.queries() as q:
        q.associate_schedule_entity(schedule_id, entity_id)
