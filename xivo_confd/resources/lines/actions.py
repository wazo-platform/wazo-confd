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
from flask import request
from flask.helpers import make_response
from flask_negotiate import produces

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int, Unicode
from xivo_confd.resources.lines import actions_sip
from xivo_dao.data_handler.line import services as line_services
from xivo_dao.data_handler.line.model import Line


def load(core_rest_api):
    blueprint = Blueprint('lines', __name__, url_prefix='/%s/lines' % config.API_VERSION)
    document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('context', Unicode()),
        Field('name', Unicode()),
        Field('protocol', Unicode()),
        Field('provisioning_extension', Unicode()),
        Field('device_slot', Int()),
        Field('device_id', Unicode()),
    )
    converter = Converter.for_resource(document, Line)

    @blueprint.route('')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def list():
        if 'q' in request.args:
            lines = line_services.find_all_by_name(request.args['q'])
        else:
            lines = line_services.find_all()

        items = converter.encode_list(lines)
        return make_response(items, 200)

    @blueprint.route('/<int:resource_id>')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get(resource_id):
        line = line_services.get(resource_id)
        encoded_line = converter.encode(line)
        return make_response(encoded_line, 200)

    actions_sip.load(core_rest_api)

    core_rest_api.register(blueprint)
