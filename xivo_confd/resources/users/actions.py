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

from flask import url_for, request, make_response

from xivo_confd.helpers.common import extract_search_parameters
from xivo_dao.data_handler.user import services as user_services

from .converter import user_converter, directory_converter
from .routes import route


logger = logging.getLogger(__name__)


@route('')
def list():
    if 'q' in request.args:
        items = user_services.find_all_by_fullname(request.args['q'])
        encoded_items = user_converter.encode_list(items)
        return make_response(encoded_items, 200)

    parameters = extract_search_parameters(request.args, ['view'])
    search_result = user_services.search(**parameters)

    converter = _find_converter()
    encoded_result = converter.encode_list(search_result.items, search_result.total)
    return make_response(encoded_result, 200)


def _find_converter():
    if request.args.get('view') == 'directory':
        return directory_converter
    return user_converter


@route('/<int:resource_id>')
def get(resource_id):
    user = user_services.get(resource_id)
    encoded_user = user_converter.encode(user)
    return make_response(encoded_user, 200)


@route('', methods=['POST'])
def create():
    user = user_converter.decode(request)
    created_user = user_services.create(user)
    encoded_user = user_converter.encode(created_user)
    location = url_for('.get', resource_id=created_user.id)
    return make_response(encoded_user, 201, {'Location': location})


@route('/<int:resource_id>', methods=['PUT'])
def edit(resource_id):
    user = user_services.get(resource_id)
    user_converter.update(request, user)
    user_services.edit(user)
    return make_response('', 204)


@route('/<int:resource_id>', methods=['DELETE'])
def delete(resource_id):
    user = user_services.get(resource_id)
    user_services.delete(user)
    return make_response('', 204)
