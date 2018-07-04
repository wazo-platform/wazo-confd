# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(queue_id, user_id, **kwargs):
    check = kwargs.pop('check', True)
    response = confd.queues(queue_id).members.users(user_id).put(**kwargs)
    if check:
        response.assert_ok()


def dissociate(queue_id, user_id, **kwargs):
    check = kwargs.get('check', True)
    response = confd.queues(queue_id).members.users(user_id).delete()
    if check:
        response.assert_ok()
