# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.alchemy.agent_login_status import AgentLoginStatus
from xivo_dao.helpers.db_manager import Session


def find_by(**kwargs):
    return Session.query(AgentLoginStatus).filter_by(**kwargs).first()
