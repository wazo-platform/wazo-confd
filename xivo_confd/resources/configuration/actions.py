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

from flask import Blueprint
from flask import Response
from flask import request
from flask_negotiate import consumes
from flask_negotiate import produces
from xivo_dao.data_handler.configuration import services

from xivo_confd import config
from xivo_confd.helpers import serializer
from xivo_confd.helpers.mooltiparse import Field, Boolean


def load(core_rest_api):
    blueprint = Blueprint('configuration',
                          __name__,
                          url_prefix='/%s/configuration' % config.API_VERSION)
    document = core_rest_api.content_parser.document(Field('enabled', Boolean()))

    @blueprint.route('/live_reload', methods=['GET'])
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get_live_reload():
        result = services.get_live_reload_status()
        response = serializer.encode(result)
        return Response(response=response,
                        status=200,
                        content_type='application/json')

    @blueprint.route('/live_reload', methods=['PUT'])
    @core_rest_api.auth.login_required
    @consumes('application/json')
    def set_live_reload():
        data = document.parse(request)
        services.set_live_reload_status(data)
        return Response(status=204)

    core_rest_api.register(blueprint)
