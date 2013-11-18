# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging

from . import mapper
from .routes import line_route as route
from ..user_links.actions import formatter as user_link_formatter

from flask.globals import request
from flask.helpers import make_response
from xivo_dao.data_handler.line.model import Line
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.user_line_extension import services as ule_services
from xivo_restapi.helpers import serializer
from xivo_restapi.helpers.formatter import Formatter


logger = logging.getLogger(__name__)
formatter = Formatter(mapper, serializer, Line)


@route('')
def list():
    if 'q' in request.args:
        lines = line_services.find_all_by_name(request.args['q'])
    else:
        lines = line_services.find_all()

    result = formatter.list_to_api(lines)
    return make_response(result, 200)


@route('/<int:lineid>')
def get(lineid):
    line = line_services.get(lineid)
    result = formatter.to_api(line)
    return make_response(result, 200)


@route('/<int:lineid>/user_links')
def list_user_links(lineid):
    line = ule_services.find_all_by_line_id(lineid)
    result = user_link_formatter.list_to_api(line)
    return make_response(result, 200)
