# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import db


def associate(context_name, entity_name, check=True):
    with db.queries() as q:
        q.associate_context_entity(context_name, entity_name)
