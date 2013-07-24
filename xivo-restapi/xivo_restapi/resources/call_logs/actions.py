# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
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
from datetime import datetime
from flask import Blueprint
from flask.globals import request
from flask.helpers import make_response
from xivo_dao.data_handler.call import services as call_services
from xivo_restapi import config
from xivo_restapi.helpers.route_generator import RouteGenerator
from xivo_restapi.resources.call_logs import mapper


logger = logging.getLogger(__name__)
blueprint = Blueprint('call_logs', __name__, url_prefix='/%s/call_logs' % config.VERSION_1_1)
route = RouteGenerator(blueprint, content_type='text/csv')


@route('/')
def list():
    start = end = None
    if 'start' in request.args:
        start = datetime.strptime('%Y:%m:dT%H:%M:%S', request.args['start'])
    if 'end' in request.args:
        end = datetime.strptime('%Y:%m:dT%H:%M:%S', request.args['end'])

    calls = call_services.find_all(start, end)

    result = mapper.encode_list(calls)
    return make_response(result, 200)
