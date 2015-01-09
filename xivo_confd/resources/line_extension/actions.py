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
    extension_blueprint = core_rest_api.blueprint('extensions')
    document = core_rest_api.content_parser.document(
        Field('line_id', Int()),
        Field('extension_id', Int())
    )
    converter = Converter.for_request(document, LineExtension, {'lines': 'line_id', 'extensions': 'extension_id'})

    @line_blueprint.route('/<int:line_id>/extension', methods=['POST'])
    @core_rest_api.auth.login_required
    @produces('application/json')
    @consumes('application/json')
    def associate_extension(line_id):
        url.check_line_exists(line_id)
        line_extension = converter.decode(request)
        created_line_extension = line_extension_services.associate(line_extension)
        encoded_line_extension = converter.encode(created_line_extension)
        location = url_for('.associate_extension', line_id=line_id)
        return make_response(encoded_line_extension, 201, {'Location': location})

    @line_blueprint.route('/<int:line_id>/extension')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get_extension_from_line(line_id):
        url.check_line_exists(line_id)
        line_extension = line_extension_services.get_by_line_id(line_id)
        encoded_line_extension = converter.encode(line_extension)
        return make_response(encoded_line_extension, 200)

    @line_blueprint.route('/<int:line_id>/extension', methods=['DELETE'])
    @core_rest_api.auth.login_required
    def dissociate_extension(line_id):
        url.check_line_exists(line_id)
        line_extension = line_extension_services.get_by_line_id(line_id)
        line_extension_services.dissociate(line_extension)
        return make_response('', 204)

    @extension_blueprint.route('/<int:extension_id>/line')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get_line_from_extension(extension_id):
        url.check_extension_exists(extension_id)
        line_extension = line_extension_services.get_by_extension_id(extension_id)
        encoded_line_extension = converter.encode(line_extension)
        return make_response(encoded_line_extension, 200)

    core_rest_api.register(line_blueprint)
    core_rest_api.register(extension_blueprint)
