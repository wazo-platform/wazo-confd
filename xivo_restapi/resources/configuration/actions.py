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
from xivo_restapi.resources.configuration.routes import blueprint
from xivo_restapi.flask_http_server import content_parser
from xivo_restapi.helpers.route_generator import RouteGenerator
from xivo_restapi.helpers import serializer
from xivo_restapi.helpers.premacop import Field, types

from xivo_dao.data_handler.configuration import services
from flask.helpers import make_response
from flask.globals import request

route = RouteGenerator(blueprint)

config_document = content_parser.document(Field('enabled', types.Boolean()))


@route('/live_reload', methods=['GET'])
def get_live_reload():
    result = services.get_live_reload_status()
    return make_response(serializer.encode(result), 200)


@route('/live_reload', methods=['PUT'])
def set_live_reload():
    data = config_document.parse(request)
    services.set_live_reload_status(data)
    return make_response('', 204)
