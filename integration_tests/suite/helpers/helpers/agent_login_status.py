# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from . import db


def generate_agent_login_status(**parameters):
    return add_agent_login_status(**parameters)


def add_agent_login_status(**parameters):
    with db.queries() as queries:
        agent_id = queries.insert_agent_login_status(**parameters)
    return {'agent_id': agent_id,
            'id': agent_id}


def delete_agent_login_status(agent_id, check=False):
    with db.queries() as queries:
        queries.delete_agent_login_status(agent_id)
