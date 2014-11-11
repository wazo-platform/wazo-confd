# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Avencall
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

from flask import make_response, Blueprint

from xivo_confd import config
from xivo_confd.helpers.route_generator import RouteGenerator
from xivo_dao.data_handler.infos import services as infos_services
from xivo_dao.data_handler.infos.model import Infos

from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Unicode

from xivo_confd.helpers.converter import Converter

logger = logging.getLogger(__name__)
blueprint = Blueprint('infos', __name__, url_prefix='/%s/infos' % config.VERSION_1_1)
route = RouteGenerator(blueprint)

document = content_parser.document(Field('uuid', Unicode()))

converter = Converter.for_document(document, Infos, 'infos', 'uuid')


@route('')
def get():
    return make_response(converter.encode(infos_services.get()), 200)
