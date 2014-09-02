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

from xivo_dao.data_handler.line_extension import services as line_extension_services

from xivo_confd.helpers import url
from xivo_confd.resources.lines.routes import line_route
from xivo_confd.resources.extensions.routes import extension_route

from xivo_confd.resources.line_extension.formatter import LineExtensionFormatter

from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Int

formatter = LineExtensionFormatter()

document = content_parser.document(
    Field('line_id', Int()),
    Field('extension_id', Int())
)


@line_route('/<int:lineid>/extension', methods=['POST'])
def associate_extension(lineid):
    url.check_line_exists(lineid)
    data = document.parse(request)
    model = formatter.dict_to_model(data, lineid)
    created_model = line_extension_services.associate(model)

    result = formatter.to_api(created_model)
    location = url_for('.associate_extension', lineid=lineid)
    return make_response(result, 201, {'Location': location})


@line_route('/<int:lineid>/extension')
def get_extension_from_line(lineid):
    url.check_line_exists(lineid)
    line_extension = line_extension_services.get_by_line_id(lineid)
    result = formatter.to_api(line_extension)
    return make_response(result, 200)


@extension_route('/<int:extensionid>/line')
def get_line_from_extension(extensionid):
    url.check_extension_exists(extensionid)
    line_extension = line_extension_services.get_by_extension_id(extensionid)
    result = formatter.to_api(line_extension)
    return make_response(result, 200)


@line_route('/<int:lineid>/extension', methods=['DELETE'])
def dissociate_extension(lineid):
    url.check_line_exists(lineid)
    line_extension = line_extension_services.get_by_line_id(lineid)
    line_extension_services.dissociate(line_extension)
    return make_response('', 204)
