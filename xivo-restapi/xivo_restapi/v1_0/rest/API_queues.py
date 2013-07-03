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

from flask import request
from flask.helpers import make_response
from xivo_restapi.v1_0 import rest_encoder
from xivo_restapi.authentication.xivo_realm_digest import realmDigest
from xivo_restapi.negotiate.flask_negotiate import produces
from xivo_restapi.v1_0.services.queue_management import QueueManagement
from xivo_restapi.v1_0.rest.helpers.global_helper import exception_catcher


logger = logging.getLogger(__name__)


class APIQueues(object):

    def __init__(self):
        self._queue_management = QueueManagement()

    @exception_catcher
    @produces('application/json')
    @realmDigest.requires_auth
    def list_queues(self):
        logger.debug("List args:" + str(request.args))
        result = self._queue_management.get_all_queues()
        logger.debug("Got result in API: " + str(result))
        result = sorted(result, key=lambda k: k.number)
        logger.debug("got result")
        body = rest_encoder.encode(result)
        logger.debug("result encoded")
        return make_response(body, 200)
