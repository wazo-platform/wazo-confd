# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import db


def associate(call_filter_id, entity_id, check=True):
    with db.queries() as q:
        q.associate_call_filter_entity(call_filter_id, entity_id)
