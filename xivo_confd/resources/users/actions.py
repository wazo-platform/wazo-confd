# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

import json

from flask import Blueprint
from flask import Response
from flask import request
from flask import url_for
from flask_negotiate import consumes
from flask_negotiate import produces
from xivo_dao.data_handler.user import services as user_services
from xivo_dao.data_handler.user.model import User, UserDirectory

from xivo_confd import config
from xivo_confd.helpers.common import extract_search_parameters
from xivo_confd.helpers.converter import Converter, Serializer, DocumentParser, DocumentMapper
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int


class DirectorySerializer(Serializer):

    def serialize(self, item):
        return json.dumps(item)

    def serialize_list(self, items, total=None):
        return json.dumps({'total': total or len(items),
                           'items': items})


def load(core_rest_api):
    blueprint = Blueprint('users', __name__, url_prefix='/%s/users' % config.API_VERSION)
    user_document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('firstname', Unicode()),
        Field('lastname', Unicode()),
        Field('caller_id', Unicode()),
        Field('outgoing_caller_id', Unicode()),
        Field('username', Unicode()),
        Field('password', Unicode()),
        Field('music_on_hold', Unicode()),
        Field('mobile_phone_number', Unicode()),
        Field('userfield', Unicode()),
        Field('timezone', Unicode()),
        Field('language', Unicode()),
        Field('description', Unicode()),
        Field('preprocess_subroutine', Unicode())
    )
    directory_document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('line_id', Int()),
        Field('agent_id', Int()),
        Field('firstname', Unicode()),
        Field('lastname', Unicode()),
        Field('exten', Unicode()),
        Field('mobile_phone_number', Unicode())
    )
    user_converter = Converter.for_resource(user_document, User)
    directory_converter = Converter(parser=DocumentParser(directory_document),
                                    mapper=DocumentMapper(directory_document),
                                    serializer=DirectorySerializer(),
                                    model=UserDirectory)

    @blueprint.route('')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get_uers():
        if 'q' in request.args:
            items = user_services.find_all_by_fullname(request.args['q'])
            response = user_converter.encode_list(items)
        else:
            parameters = extract_search_parameters(request.args, ['view'])
            search_result = user_services.search(**parameters)
            converter = _find_converter()
            response = converter.encode_list(search_result.items, search_result.total)

        return Response(response=response,
                        status=200,
                        content_type='application/json')

    def _find_converter():
        if request.args.get('view') == 'directory':
            return directory_converter
        return user_converter

    @blueprint.route('/<int:resource_id>')
    @core_rest_api.auth.login_required
    @produces('application/json')
    def get(resource_id):
        user = user_services.get(resource_id)
        response = user_converter.encode(user)
        return Response(response=response,
                        status=200,
                        content_type='application/json')

    @blueprint.route('', methods=['POST'])
    @core_rest_api.auth.login_required
    @produces('application/json')
    @consumes('application/json')
    def create():
        user = user_converter.decode(request)
        created_user = user_services.create(user)
        response = user_converter.encode(created_user)
        location = url_for('.get', resource_id=created_user.id)
        return Response(response=response,
                        status=201,
                        content_type='application/json',
                        headers={'Location': location})

    @blueprint.route('/<int:resource_id>', methods=['PUT'])
    @core_rest_api.auth.login_required
    @consumes('application/json')
    def edit(resource_id):
        user = user_services.get(resource_id)
        user_converter.update(request, user)
        user_services.edit(user)
        return Response(status=204)

    @blueprint.route('/<int:resource_id>', methods=['DELETE'])
    @core_rest_api.auth.login_required
    def delete(resource_id):
        user = user_services.get(resource_id)
        user_services.delete(user)
        return Response(status=204)

    core_rest_api.register(blueprint)
