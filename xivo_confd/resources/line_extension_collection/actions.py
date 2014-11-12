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

from xivo_confd.resources.lines.routes import line_route

from xivo_dao.data_handler.line_extension.model import LineExtension
from xivo_dao.data_handler.line_extension import services as line_extension_services

from xivo_confd.helpers import url
from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Int
from xivo_confd.helpers.converter import Converter

document = content_parser.document(
    Field('line_id', Int()),
    Field('extension_id', Int())
)

converter = Converter.for_association(document, LineExtension, {'lines': 'line_id',
                                                                'extensions': 'extension_id'})


@line_route('/<int:line_id>/extensions')
def list_extensions(line_id):
    url.check_line_exists(line_id)
    line_extensions = line_extension_services.get_all_by_line_id(line_id)
    items = converter.encode_list(line_extensions)
    return make_response(items, 200)


@line_route('/<int:line_id>/extensions', methods=['POST'])
def associate_line_extension(line_id):
    url.check_line_exists(line_id)
    model = converter.decode(request)
    created_model = line_extension_services.associate(model)
    encoded_model = converter.encode(created_model)
    location = url_for('.list_extensions', line_id=line_id)
    return make_response(encoded_model, 201, {'Location': location})


@line_route('/<int:line_id>/extensions/<int:extension_id>', methods=['DELETE'])
def dissociate_line_extension(line_id, extension_id):
    url.check_line_exists(line_id)
    url.check_extension_exists(extension_id)
    model = LineExtension(line_id=line_id, extension_id=extension_id)
    line_extension_services.dissociate(model)
    return make_response('', 204)
