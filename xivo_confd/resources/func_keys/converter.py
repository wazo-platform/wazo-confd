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

import abc
import re

from flask import url_for

from xivo_dao.helpers import errors
from xivo_confd.helpers.converter import Parser, Mapper, Builder
from xivo_dao.resources.func_key.model import FuncKeyTemplate, FuncKey

from xivo_dao.resources.func_key.model import UserDestination, \
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
        return request.json


class TemplateValidator(object):

    def __init__(self, funckey_validator):
        self.funckey_validator = funckey_validator

    DOCUMENT = Document([
        Field('id', Int()),
        Field('name', Unicode(), create=[Required()]),
        Field('description', Unicode()),
        Field('keys', Dict())
    ])

    def validate(self, mapping, action=None):
        self.DOCUMENT.validate(mapping, action)
        keys = mapping.get('keys', {})
        self.validate_keys(keys)

    def validate_keys(self, key_mapping):
        for pos, mapping in key_mapping.iteritems():
            if not isinstance(pos, int):
                raise errors.wrong_type('keys', 'numeric positions')
            if not isinstance(mapping, dict):
                raise errors.wrong_type('keys', 'dict-like structures')
            self.funckey_validator.validate(mapping)


class FuncKeyValidator(object):

    DOCUMENT = Document([
        Field('label', Unicode()),
        Field('blf', Boolean()),
        Field('destination', Dict(), create=[Required()])
    ])

    def __init__(self, builders):
        self.builders = builders

    def validate(self, mapping, action=None):
        self.DOCUMENT.validate(mapping, action)

        if 'destination' in mapping:
            self.validate_destination(mapping['destination'])

    def validate_destination(self, destination):
        dest_type = destination.get('type')

        if not dest_type:
            raise errors.param_not_found('destination', 'type')

        if dest_type not in self.builders:
            raise errors.param_not_found('destination', 'type')

        builder = self.builders[dest_type]
        builder.validate(destination)


class TemplateMapper(object):

    def __init__(self, funckey_mapper):
        self.funckey_mapper = funckey_mapper

    def for_decoding(self, mapping):
        if 'keys' in mapping:
            mapping['keys'] = {int(pos): funckey
                               for pos, funckey in mapping['keys'].iteritems()}
        return mapping

    def for_encoding(self, model):
        mapping = {field: getattr(model, field)
                   for field in model.FIELDS
                   if field != 'keys'}
        mapping['keys'] = {pos: self.funckey_mapper.for_encoding(key)
                           for pos, key in model.keys.iteritems()}
        return mapping


class FuncKeyMapper(Mapper):

    def __init__(self, builders):
        self.builders = builders

    def for_decoding(self, mapping):
        return mapping

    def for_encoding(self, model):
        mapping = {field: getattr(model, field)
                   for field in model.FIELDS
                   if field != 'destination'}
        mapping['destination'] = self.map_destination(model.destination)
        return mapping

    def map_destination(self, destination):
        builder = self.builders[destination.type]
        return builder.to_mapping(destination)


class TemplateBuilder(Builder):

    def __init__(self, validator, funckey_builder):
        self.validator = validator
        self.funckey_builder = funckey_builder

    def create(self, mapping):
        self.validator.validate(mapping, 'create')
        key_mapping = mapping.get('keys', {})
        funckeys = self.create_funckeys(key_mapping)
        return FuncKeyTemplate(name=mapping['name'],
                               description=mapping.get('description'),
                               keys=funckeys)

    def update(self, model, mapping):
        self.validator.validate(mapping, 'update')
        model.name = mapping.get('name', model.name)
        model.description = mapping.get('description', model.description)

        key_mapping = mapping.get('keys', {})
        self.update_funckeys(model.keys, key_mapping)

    def create_funckeys(self, key_mapping):
        return {pos: self.funckey_builder.create(funckey)
                for pos, funckey in key_mapping.iteritems()}

    def update_funckeys(self, old_mapping, new_mapping):
        for pos, mapping in new_mapping.iteritems():
            self.funckey_builder.update(old_mapping[pos], mapping)


class FuncKeyBuilder(Builder):

    def __init__(self, validator, builders):
        self.validator = validator
        self.builders = builders

    def create(self, mapping):
        self.validator.validate(mapping, 'create')
        destination = self.build_destination(mapping['destination'])
        return FuncKey(label=mapping.get('label'),
                       blf=mapping.get('blf', False),
                       destination=destination)

    def update(self, model, mapping):
        self.validator.validate(mapping, 'update')

        for field, value in mapping.iteritems():
            if field != 'destination':
                setattr(model, value)

        if 'destination' in mapping:
            model.destination = self.build_destination(mapping['destination'])

    def build_destination(self, destination):
        builder = self.builders[destination['type']]
        return builder.build(destination)


class DestinationBuilder(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def fields(self):
        return

    @abc.abstractproperty
    def destination(self):
        return

    @abc.abstractmethod
    def to_model(self, destination):
        pass

    def build(self, destination):
        self.validate(destination)
        return self.to_model(destination)

    def validate(self, destination):
        for field in self.fields:
            field.validate(destination.get(field.name))

    def to_mapping(self, destination):
        mapping = {field.name: getattr(field.name, destination)
                   for field in self.fields}
        mapping['type'] = self.destination
        mapping['href'] = self.url(destination)
        return mapping

    def url(self, destination):
        return None


class UserDestinationBuilder(DestinationBuilder):

    destination = 'user'

    fields = [Field('user_id', Int(), Required())]

    def to_model(self, destination):
        return UserDestination(user_id=destination['user_id'])

    def url(self, destination):
        return url_for('users.get', id=destination['user_id'], external_=True)


class GroupDestinationBuilder(DestinationBuilder):

    destination = 'group'

    fields = [Field('group_id', Int(), Required())]

    def to_model(self, destination):
        return GroupDestination(group_id=destination['group_id'])


class QueueDestinationBuilder(DestinationBuilder):

    destination = 'queue'

    fields = [Field('queue_id', Int(), Required())]

    def to_model(self, destination):
        return QueueDestination(queue_id=destination['queue_id'])


class ConferenceDestinationBuilder(DestinationBuilder):

    destination = 'conference'

    fields = [Field('conference_id', Int(), Required())]

    def to_model(self, destination):
        return ConferenceDestination(conference_id=destination['conference_id'])


class PagingDestinationBuilder(DestinationBuilder):

    destination = 'paging'

    fields = [Field('paging_id', Int(), Required())]

    def to_model(self, destination):
        return PagingDestination(paging_id=destination['paging_id'])


class BSFilterDestinationBuilder(DestinationBuilder):

    destination = 'bsfilter'

    fields = [Field('filter_member_id', Int(), Required())]

    def to_model(self, destination):
        return BSFilterDestination(filter_member_id=destination['filter_member_id'])


class ServiceDestinationBuilder(DestinationBuilder):

    destination = 'service'

    fields = [Field('service', Unicode(), Required())]

    def to_model(self, destination):
        return ServiceDestination(service=destination['service'])


class CustomDestinationBuilder(DestinationBuilder):

    destination = 'custom'

    fields = [Field('exten', Unicode(), Required(), Regexp(EXTEN_REGEX))]

    def to_model(self, destination):
        return CustomDestination(exten=destination['exten'])


class ForwardDestinationBuilder(DestinationBuilder):

    destination = 'forward'

    fields = [Field('forward',
                    Unicode(),
                    Required(), Choice(['noanswer', 'busy', 'unconditional'])),
              Field('exten',
                    Unicode(),
                    Required(), Regexp(EXTEN_REGEX))
              ]

    def to_model(self, destination):
        return ForwardDestination(forward=destination['forward'],
                                  exten=destination['exten'])


class TransferDestinationBuilder(DestinationBuilder):

    destination = 'transfer'

    fields = [Field('transfer',
                    Unicode(),
                    Required(), Choice(['blind', 'attended'])),
              Field('exten',
                    Unicode(),
                    Required(), Regexp(EXTEN_REGEX))
              ]

    def to_model(self, destination):
        return TransferDestination(transfer=destination['transfer'],
                                   exten=destination['exten'])


class ParkPositionDestinationBuilder(DestinationBuilder):

    destination = 'park_position'

    fields = [Field('position',
                    Unicode(),
                    Required(), Regexp(EXTEN_REGEX))
              ]

    def to_model(self, destination):
        return ParkPositionDestination(position=destination['position'])


class ParkingDestinationBuilder(DestinationBuilder):

    destination = 'parking'

    fields = []

    def to_model(self, destination):
        return ParkingDestination()


class AgentDestinationBuilder(DestinationBuilder):

    destination = 'agent'

    fields = [Field('action',
                    Unicode(),
                    Required(), Choice(['login', 'logoff', 'toggle'])),
              Field('agent_id', Int(), Required())]

    def to_model(self, destination):
        return AgentDestination(action=destination['action'],
                                agent_id=destination['agent_id'])
