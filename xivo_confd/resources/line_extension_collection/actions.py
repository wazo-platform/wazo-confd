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

from flask import request, url_for, make_response
from flask_negotiate import produces
from flask_negotiate import consumes

from xivo_confd.helpers import url
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int
from xivo_dao.data_handler.line_extension import services as line_extension_services
from xivo_dao.data_handler.line_extension.model import LineExtension


def load(core_rest_api):
    line_blueprint = core_rest_api.blueprint('lines')
    document = core_rest_api.content_parser.document(
        Field('line_id', Int()),
        Field('extension_id', Int())
    )
    converter = Converter.for_request(document, LineExtension, {'lines': 'line_id',
                                                                'extensions': 'extension_id'})

    @line_blueprint.route('/<int:line_id>/extensions')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def list_extensions(line_id):
        url.check_line_exists(line_id)
        line_extensions = line_extension_services.get_all_by_line_id(line_id)
        items = converter.encode_list(line_extensions)
        return make_response(items, 200)

    @line_blueprint.route('/<int:line_id>/extensions', methods=['POST'])
    @core_rest_api.auth.login_required
    @produces('application/json')
    @consumes('application/json')
    def associate_line_extension(line_id):
        url.check_line_exists(line_id)
        model = converter.decode(request)
        created_model = line_extension_services.associate(model)
        encoded_model = converter.encode(created_model)
        location = url_for('.list_extensions', line_id=line_id)
        return make_response(encoded_model, 201, {'Location': location})

    @line_blueprint.route('/<int:line_id>/extensions/<int:extension_id>', methods=['DELETE'])
    @core_rest_api.auth.login_required
    def dissociate_line_extension(line_id, extension_id):
        url.check_line_exists(line_id)
        url.check_extension_exists(extension_id)
        model = LineExtension(line_id=line_id, extension_id=extension_id)
        line_extension_services.dissociate(model)
        return make_response('', 204)

    core_rest_api.register(line_blueprint)
