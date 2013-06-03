# -*- coding: UTF-8 -*-
#
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import logging

from xivo_dao import agent_dao
from xivo_restapi.restapi_config import RestAPIConfig

data_access_logger = logging.getLogger(RestAPIConfig.DATA_ACCESS_LOGGERNAME)


class AgentManagement(object):

    def get_all_agents(self):
        result = agent_dao.all()
        if result is not None:
            return result
        return False
