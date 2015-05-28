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

from xivo_dao.helpers import errors
from xivo_confd.helpers.converter import Parser, Mapper, Builder
from xivo_confd.resources.func_keys.model import FuncKeyTemplate, FuncKey


from xivo_confd.helpers.mooltiparse import Document, Field, \
    Int, Boolean, Unicode, Dict, \
    Required, Choice, Regexp



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

    __metaclass__  = abc.ABCMeta

    def build(self, destination):
        self.validate(destination)
        return self.convert(destination)

    @abc.abstractmethod
    def validate(self, destination):
        pass

    @abc.abstractmethod
    def convert(self, destination):
        pass
