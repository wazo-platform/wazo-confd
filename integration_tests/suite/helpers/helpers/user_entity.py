# -*- coding: UTF-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import db


def associate(user_id, entity_id, check=True):
    with db.queries() as q:
        q.associate_user_entity(user_id, entity_id)
