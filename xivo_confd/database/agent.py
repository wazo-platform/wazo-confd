# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.agentfeatures import AgentFeatures as Agent
from xivo_dao.helpers.db_manager import Session


def agent_id_exists(agent_id):
    query = (Session.query(Agent)
             .filter_by(id=agent_id)
             .exists())

    return Session.query(query).scalar()


def find_by(**kwargs):
    return Session.query(Agent).filter_by(**kwargs).first()
