# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import db


def associate(queue_id, extension_id, check=True):
    with db.queries() as q:
        q.associate_queue_extension(queue_id, extension_id)


def dissociate(queue_id, extension_id, check=True):
    with db.queries() as q:
        q.dissociate_queue_extension(queue_id, extension_id)
