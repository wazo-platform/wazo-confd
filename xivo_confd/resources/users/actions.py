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
from flask import request
from xivo_confd.resources.users import services as user_services
from xivo_dao.resources.user.model import User, UserDirectory

from xivo_confd import config
from xivo_confd.helpers.common import extract_search_parameters
from xivo_confd.helpers.converter import Converter, Serializer, DocumentParser, DocumentMapper, ModelBuilder
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int
from xivo_confd.helpers.resource import CRUDResource, DecoratorChain, build_response


class DirectorySerializer(Serializer):

    def serialize(self, item):
        return json.dumps(item)

    def serialize_list(self, items, total=None):
        return json.dumps({'total': total or len(items),
                           'items': items})


class UserResource(CRUDResource):

    def __init__(self, service, converter, directory_converter):
        super(UserResource, self).__init__(service, converter)
        self.directory_converter = directory_converter

    def search(self):
        if 'q' in request.args:
            return self.search_by_fullname(request.args['q'])
        else:
            args = extract_search_parameters(request.args, ['view'])
            return self.search_by_view(args)

    def search_by_fullname(self, fullname):
        items = self.service.find_all_by_fullname(fullname)
        response = self.converter.encode_list(items)
        return build_response(response)

    def search_by_view(self, args):
        search_result = self.service.search(**args)
        converter = self.find_converter(args.get('view'))
        response = converter.encode_list(search_result.items, search_result.total)
        return build_response(response)

    def find_converter(self, view=None):
        if view == 'directory':
            return self.directory_converter
        return self.converter


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

    user_converter = Converter.resource(user_document, User)
    directory_converter = Converter(parser=DocumentParser(directory_document),
                                    mapper=DocumentMapper(directory_document, UserDirectory),
                                    serializer=DirectorySerializer(),
                                    builder=ModelBuilder(directory_document, UserDirectory))

    resource = UserResource(user_services, user_converter, directory_converter)
    DecoratorChain.register_scrud(core_rest_api, blueprint, resource)
