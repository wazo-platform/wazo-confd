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

from flask import request
from flask.helpers import make_response
from xivo_restapi.rest.authentication.xivo_realm_digest import realmDigest
from xivo_restapi.rest.negotiate.flask_negotiate import produces
from xivo_restapi.services.agent_management import AgentManagement
import logging
import rest_encoder
from xivo_restapi.rest.helpers.global_helper import exception_catcher


logger = logging.getLogger(__name__)


class APIAgents(object):

    def __init__(self):
        self._agent_management = AgentManagement()

    @exception_catcher
    @produces('application/json')
    @realmDigest.requires_auth
    def list_agents(self):
        logger.debug("List args:" + str(request.args))
        result = self._agent_management.get_all_agents()
        result = sorted(result, key=lambda k: k.number)
        logger.debug("got result")
        body = rest_encoder.encode(result)
        logger.debug("result encoded")
        return make_response(body, 200)
