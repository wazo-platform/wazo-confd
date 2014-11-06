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

from flask import url_for
from flask.globals import request
from flask.helpers import make_response

from xivo_dao.data_handler.user import services as user_services
from xivo_dao.data_handler.user.model import User, UserDirectoryView
from xivo_confd.helpers import serializer
from xivo_confd.helpers.common import extract_search_parameters
from xivo_confd.helpers.formatter import NewFormatter

from .routes import route
from . import views
from xivo_dao.data_handler import errors


logger = logging.getLogger(__name__)

user_formatter = NewFormatter(view_document=views.user_document,
                              serializer=serializer,
                              model_class=User,
                              links_func=views.user_location)
user_directory_formatter = NewFormatter(view_document=views.user_directory_document,
                                        serializer=serializer,
                                        model_class=UserDirectoryView,
                                        links_func=views.user_directory_location)


@route('')
def list():
    if 'view' in request.args:
        result = _find_all_by_view(request.args['view'])
    else:
        if 'q' in request.args:
            items = user_services.find_all_by_fullname(request.args['q'])
            total = len(items)
        else:
            parameters = extract_search_parameters(request.args)
            search_result = user_services.search(**parameters)
            items = search_result.items
            total = search_result.total
        result = user_formatter.list_to_api(items, total)
    return make_response(result, 200)


def _find_all_by_view(view):
    result = None
    if view == 'directory':
        items = user_services.find_all_by_view_directory()
        result = user_directory_formatter.list_to_api(items, len(items))
    else:
        raise errors.invalid_query_parameter('view', view)
    return result


@route('/<int:userid>')
def get(userid):
    user = user_services.get(userid)
    result = user_formatter.to_api(user)
    return make_response(result, 200)


@route('', methods=['POST'])
def create():
    data = views.user_document.parse(request)
    user = user_formatter.dict_to_model(data)
    user = user_services.create(user)
    result = user_formatter.to_api(user)
    location = url_for('.get', userid=user.id)
    return make_response(result, 201, {'Location': location})


@route('/<int:userid>', methods=['PUT'])
def edit(userid):
    data = views.user_document.parse(request)
    user = user_services.get(userid)
    user_formatter.update_dict_model(data, user)
    user_services.edit(user)
    return make_response('', 204)


@route('/<int:userid>', methods=['DELETE'])
def delete(userid):
    user = user_services.get(userid)
    user_services.delete(user)
    return make_response('', 204)
