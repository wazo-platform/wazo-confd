# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import confd


def associate(queue_id, agent_id, **kwargs):
    check = kwargs.pop('check', True)
    kwargs['agent_id'] = agent_id
    response = confd.queues(queue_id).members.agents.post(**kwargs)
    if check:
        response.assert_ok()


def dissociate(queue_id, agent_id, **kwargs):
    check = kwargs.get('check', True)
    response = confd.queues(queue_id).members.agents(agent_id).delete()
    if check:
        response.assert_ok()
