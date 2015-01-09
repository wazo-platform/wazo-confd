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

from flask import make_response, Blueprint
from flask_negotiate import produces

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Unicode
from xivo_dao.data_handler.infos import services as infos_services
from xivo_dao.data_handler.infos.model import Infos


def load(core_rest_api):
    blueprint = Blueprint('infos', __name__, url_prefix='/%s/infos' % config.API_VERSION)
    document = core_rest_api.content_parser.document(Field('uuid', Unicode()))

    converter = Converter.for_resource(document, Infos, 'infos', 'uuid')

    @blueprint.route('')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get():
        return make_response(converter.encode(infos_services.get()), 200)

    core_rest_api.register(blueprint)
