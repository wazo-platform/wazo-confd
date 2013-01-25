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
from xivo_restapi.services.queue_management import QueueManagement
import logging
import rest_encoder


logger = logging.getLogger(__name__)


class APIQueues(object):

    def __init__(self):
        self._queue_management = QueueManagement()

    def list_queues(self):
        try:
            logger.debug("List args:" + str(request.args))
            result = self._queue_management.get_all_queues()
            result = sorted(result, key=lambda k: k['number'])
            logger.debug("got result")
            body = rest_encoder.encode(result)
            logger.debug("result encoded")
            return make_response(body, 200)

        except Exception as e:
            logger.debug("got exception:" + str(e.args))
            return make_response(str(e.args), 500)
