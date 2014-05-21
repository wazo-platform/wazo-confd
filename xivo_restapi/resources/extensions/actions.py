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

import logging

from . import mapper

from flask import url_for, request
from flask.helpers import make_response
from xivo_dao.data_handler.extension import services as extension_services
from xivo_dao.data_handler.extension.model import Extension, ExtensionOrdering
from xivo_restapi.helpers import serializer
from xivo_restapi.helpers.common import extract_find_parameters
from xivo_restapi.helpers.formatter import Formatter
from xivo_restapi.resources.extensions.routes import extension_route as route


logger = logging.getLogger(__name__)
formatter = Formatter(mapper, serializer, Extension)


order_mapping = {'exten': ExtensionOrdering.exten,
                 'context': ExtensionOrdering.context}


@route('')
def list():
    parameters = extract_find_parameters(order_mapping)
    search_result = extension_services.search(**parameters)
    result = formatter.list_to_api(search_result.items, search_result.total)
    return make_response(result, 200)


@route('/<int:extensionid>')
def get(extensionid):
    extension = extension_services.get(extensionid)
    result = formatter.to_api(extension)
    return make_response(result, 200)


@route('', methods=['POST'])
def create():
    data = request.data.decode("utf-8")
    extension = formatter.to_model(data)
    extension = extension_services.create(extension)
    result = formatter.to_api(extension)
    location = url_for('.get', extensionid=extension.id)
    return make_response(result, 201, {'Location': location})


@route('/<int:extensionid>', methods=['PUT'])
def edit(extensionid):
    data = request.data.decode("utf-8")
    extension = extension_services.get(extensionid)
    formatter.update_model(data, extension)
    extension_services.edit(extension)
    return make_response('', 204)


@route('/<int:extensionid>', methods=['DELETE'])
def delete(extensionid):
    extension = extension_services.get(extensionid)
    extension_services.delete(extension)
    return make_response('', 204)
