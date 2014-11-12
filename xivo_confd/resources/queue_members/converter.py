# -*- coding: utf-8 -*-

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

from xivo_dao.data_handler.queue_members.model import QueueMemberAgent

from xivo_confd.helpers.converter import Converter, Serializer, AssociationParser, DocumentMapper
from xivo_confd.flask_http_server import content_parser
from xivo_confd.helpers.mooltiparse import Field, Int


class PlainSerializer(Serializer):

    def serialize(self, mapping):
        return json.dumps(mapping)

    def serialize_list(self, items, total=None):
        return json.dumps(items)


document = content_parser.document(
    Field('queue_id', Int()),
    Field('agent_id', Int()),
    Field('penalty', Int())
)


converter = Converter(parser=AssociationParser(document),
                      mapper=DocumentMapper(document),
                      serializer=PlainSerializer(),
                      model=QueueMemberAgent)
