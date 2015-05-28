# -*- coding: UTF-8 -*-

# Copyright (C) 2013-2015 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

import json
import abc
import re

from xivo_dao.helpers import errors
from xivo_confd.helpers.converter import Parser, Mapper, Builder
from xivo_confd.resources.func_keys.model import FuncKeyTemplate, FuncKey

from xivo_confd.resources.func_keys.model import UserDestination, \
    GroupDestination, QueueDestination, ConferenceDestination, \
    PagingDestination, BSFilterDestination, ServiceDestination, \
    CustomDestination, ForwardDestination, TransferDestination, \
    ParkPositionDestination, ParkingDestination, AgentDestination

from xivo_confd.helpers.mooltiparse import Document, Field, \
    Int, Boolean, Unicode, Dict, \
    Required, Choice, Regexp


EXTEN_REGEX = re.compile(r'[A-Z0-9+*]+')


class JsonParser(Parser):

    def parse(self, request):
        return json.loads(request.body)


class JsonMapper(Mapper):

    def for_encoding(self, mapping):
        return mapping

    def for_decoding(self, mapping):
        return mapping


class TemplateBuilder(Builder):

    TEMPLATE_DOC = Document([
        Field('name', Unicode(), create=[Required()]),
        Field('description', Unicode()),
        Field('keys', Dict())
    ])

    FUNCKEY_DOC = Document([
        Field('label', Unicode()),
        Field('blf', Boolean()),
        Field('destination', Dict(), Required())
    ])

    def __init__(self, destination_builders):
        self.destination_builders = destination_builders

    def create(self, mapping):
        self.TEMPLATE_DOC.validate(mapping, 'create')

        key_mapping = mapping.get('keys', {})
        funckeys = self.build_funckeys(key_mapping)

        return FuncKeyTemplate(name=mapping['name'],
                               description=mapping.get('description'),
                               keys=funckeys)

    def update(self, model, mapping):
        self.TEMPLATE_DOC.validate(mapping)

        key_mapping = mapping.get('keys', {})
        funckeys = self.build_funckeys(key_mapping)

        model.name = mapping.get('name', model.name)
        model.description = mapping.get('description', model.description)
        model.keys.update(funckeys)

    def build_funckeys(self, key_mapping):
        self.validate_keys(key_mapping)
        keys = {pos: self.build_funckey(pos, mapping)
                for pos, mapping in key_mapping.iteritems()}
        return keys

    def validate_keys(self, key_mapping):
        for pos, mapping in key_mapping.iteritems():
            if not isinstance(mapping, dict):
                raise errors.wrong_type('keys', 'dict-like structure')
            elif not isinstance(pos, int):
                raise errors.wrong_type('keys', 'numeric positions')

            self.FUNCKEY_DOC.validate(mapping)

            dest_type = mapping['destination'].get('type')
            if not dest_type:
                raise errors.param_not_found('keys.{}.destination'.format(pos),
                                             'type')

            if dest_type not in self.destination_builders:
                raise errors.invalid_destination_type(dest_type)

    def build_funckey(self, position, mapping):
        destination = self.build_destination(mapping['destination'])
        funckey = FuncKey(position=position,
                          label=mapping.get('label'),
                          blf=mapping.get('blf', False),
                          destination=destination)
        return funckey

    def build_destination(self, destination):
        builder = self.destination_builders[destination['type']]
        return builder.build(destination)


class DestinationBuilder(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def fields(self):
        return

    def build(self, destination):
        self.validate(destination)
        return self.convert(destination)

    def validate(self, destination):
        for field in self.fields:
            field.validate(destination.get(field.name))

    @abc.abstractmethod
    def convert(self, destination):
        pass


class UserDestinationBuilder(DestinationBuilder):

    fields = [Field('user_id', Int(), Required())]

    def convert(self, destination):
        return UserDestination(user_id=destination['user_id'])


class GroupDestinationBuilder(DestinationBuilder):

    fields = [Field('group_id', Int(), Required())]

    def convert(self, destination):
        return GroupDestination(group_id=destination['group_id'])


class QueueDestinationBuilder(DestinationBuilder):

    fields = [Field('queue_id', Int(), Required())]

    def convert(self, destination):
        return QueueDestination(queue_id=destination['queue_id'])


class ConferenceDestinationBuilder(DestinationBuilder):

    fields = [Field('conference_id', Int(), Required())]

    def convert(self, destination):
        return ConferenceDestination(conference_id=destination['conference_id'])


class PagingDestinationBuilder(DestinationBuilder):

    fields = [Field('paging_id', Int(), Required())]

    def convert(self, destination):
        return PagingDestination(paging_id=destination['paging_id'])


class BSFilterDestinationBuilder(DestinationBuilder):

    fields = [Field('filter_member_id', Int(), Required())]

    def convert(self, destination):
        return BSFilterDestination(filter_member_id=destination['filter_member_id'])


class ServiceDestinationBuilder(DestinationBuilder):

    fields = [Field('service', Unicode(), Required())]

    def convert(self, destination):
        return ServiceDestination(service=destination['service'])


class CustomDestinationBuilder(DestinationBuilder):

    fields = [Field('exten', Unicode(), Required(), Regexp(EXTEN_REGEX))]

    def convert(self, destination):
        return CustomDestination(exten=destination['exten'])


class ForwardDestinationBuilder(DestinationBuilder):

    fields = [Field('forward',
                    Unicode(),
                    Required(), Choice(['noanswer', 'busy', 'unconditional'])),
              Field('exten',
                    Unicode(),
                    Required(), Regexp(EXTEN_REGEX))
              ]

    def convert(self, destination):
        return ForwardDestination(forward=destination['forward'],
                                  exten=destination['exten'])


class TransferDestinationBuilder(DestinationBuilder):

    fields = [Field('transfer',
                    Unicode(),
                    Required(), Choice(['blind', 'attended'])),
              Field('exten',
                    Unicode(),
                    Required(), Regexp(EXTEN_REGEX))
              ]

    def convert(self, destination):
        return TransferDestination(transfer=destination['transfer'],
                                   exten=destination['exten'])


class ParkPositionDestinationBuilder(DestinationBuilder):

    fields = [Field('position',
                    Unicode(),
                    Required(), Regexp(EXTEN_REGEX))
              ]

    def convert(self, destination):
        return ParkPositionDestination(position=destination['position'])


class ParkingDestinationBuilder(DestinationBuilder):

    fields = []

    def convert(self, destination):
        return ParkingDestination()


class AgentDestinationBuilder(DestinationBuilder):

    fields = [Field('action',
                    Unicode(),
                    Required(), Choice(['login', 'logoff', 'toggle'])),
              Field('agent_id', Int(), Required())]

    def convert(self, destination):
        return AgentDestination(action=destination['action'],
                                agent_id=destination['agent_id'])
