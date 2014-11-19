# -*- coding: UTF-8 -*-
#
# Copyright (C) 2014 Avencall
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

from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Unicode, Int
from xivo_confd.helpers.converter import Converter, Serializer, DocumentParser, DocumentMapper
from xivo_dao.data_handler.user.model import User, UserDirectory


class DirectorySerializer(Serializer):

    def serialize(self, item):
        return json.dumps(item)

    def serialize_list(self, items, total=None):
        return json.dumps({'total': total or len(items),
                           'items': items})


user_document = content_parser.document(
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


directory_document = content_parser.document(
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
