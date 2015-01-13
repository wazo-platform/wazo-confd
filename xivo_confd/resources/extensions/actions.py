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
from flask import url_for
from flask_negotiate import consumes
from flask_negotiate import produces
from xivo_dao.data_handler.extension import services as extension_services
from xivo_dao.data_handler.extension.model import Extension

from xivo_confd import config
from xivo_confd.helpers.common import extract_search_parameters
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int, Unicode, Boolean


def load(core_rest_api):
    blueprint = Blueprint('extensions', __name__, url_prefix='/%s/extensions' % config.API_VERSION)
    extra_parameters = ['type']

    document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('exten', Unicode()),
        Field('context', Unicode()),
        Field('commented', Boolean())
    )

    converter = Converter.for_resource(document, Extension)

    @blueprint.route('')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def list():
        parameters = extract_search_parameters(request.args, extra_parameters)
        search_result = extension_services.search(**parameters)
        response = converter.encode_list(search_result.items, search_result.total)
        return Response(response=response,
                        status=200,
                        content_type='application/json')

    @blueprint.route('/<int:resource_id>')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get(resource_id):
        extension = extension_services.get(resource_id)
        response = converter.encode(extension)
        return Response(response=response,
                        status=200,
                        content_type='application/json')

    @blueprint.route('', methods=['POST'])
    @core_rest_api.auth.login_required
    @produces('application/json')
    @consumes('application/json')
    def create():
        extension = converter.decode(request)
        created_extension = extension_services.create(extension)
        response = converter.encode(created_extension)
        location = url_for('.get', resource_id=created_extension.id)

        return Response(response=response,
                        status=201,
                        headers={'Location': location},
                        content_type='application/json')

    @blueprint.route('/<int:resource_id>', methods=['PUT'])
    @core_rest_api.auth.login_required
    @consumes('application/json')
    def edit(resource_id):
        extension = extension_services.get(resource_id)
        converter.update(request, extension)
        extension_services.edit(extension)
        return Response(status=204)

    @blueprint.route('/<int:resource_id>', methods=['DELETE'])
    @core_rest_api.auth.login_required
    def delete(resource_id):
        extension = extension_services.get(resource_id)
        extension_services.delete(extension)
        return Response(status=204)

    core_rest_api.register(blueprint)
