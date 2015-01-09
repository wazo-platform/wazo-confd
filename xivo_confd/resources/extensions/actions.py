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
from flask import url_for, request
from flask.helpers import make_response

from xivo_confd import config
from xivo_confd.helpers.common import extract_search_parameters
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int, Unicode, Boolean
from xivo_dao.data_handler.extension import services as extension_services
from xivo_dao.data_handler.extension.model import Extension


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
    def list():
        parameters = extract_search_parameters(request.args, extra_parameters)
        search_result = extension_services.search(**parameters)
        items = converter.encode_list(search_result.items, search_result.total)
        return make_response(items, 200)

    @blueprint.route('/<int:resource_id>')
    @core_rest_api.auth.login_required
    def get(resource_id):
        extension = extension_services.get(resource_id)
        encoded_extension = converter.encode(extension)
        return make_response(encoded_extension, 200)

    @blueprint.route('', methods=['POST'])
    @core_rest_api.auth.login_required
    def create():
        extension = converter.decode(request)
        created_extension = extension_services.create(extension)
        encoded_extension = converter.encode(created_extension)
        location = url_for('.get', resource_id=created_extension.id)

        return make_response(encoded_extension, 201, {'Location': location})

    @blueprint.route('/<int:resource_id>', methods=['PUT'])
    @core_rest_api.auth.login_required
    def edit(resource_id):
        extension = extension_services.get(resource_id)
        converter.update(request, extension)
        extension_services.edit(extension)
        return make_response('', 204)

    @blueprint.route('/<int:resource_id>', methods=['DELETE'])
    @core_rest_api.auth.login_required
    def delete(resource_id):
        extension = extension_services.get(resource_id)
        extension_services.delete(extension)
        return make_response('', 204)

    core_rest_api.register(blueprint)
