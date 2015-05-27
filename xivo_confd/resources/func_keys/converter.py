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
from xivo_confd.resources.func_keys.model import FuncKeyTemplate


class JsonParser(Parser):

    def parse(self, request):
        return json.loads(request.body)


class JsonMapper(Mapper):

    def for_encoding(self, mapping):
        return mapping

    def for_decoding(self, mapping):
        return mapping


class TemplateBuilder(Builder):

    REQUIRED = ('name', )

    VALID = ('name',
             'description',
             'keys')

    def __init__(self, destination_builders):
        self.destination_builders = destination_builders

    def create(self, mapping):
        self.validate_required(mapping)
        self.validate_unknown(mapping)
        funckeys = mapping.get('keys', {})
        built_keys = self.build_destinations(funckeys)
        return FuncKeyTemplate(name=mapping['name'],
                               description=mapping.get('description'),
                               keys=built_keys)

    def update(self, mapping):
        pass

    def validate_required(self, mapping):
        missing = [f for f in self.REQUIRED if f not in mapping]
        if missing:
            raise errors.missing(*missing)

    def validate_unknown(self, mapping):
        unknown = set(mapping.keys()) - set(self.VALID)
        if unknown:
            raise errors.unknown(*unknown)

    def build_destinations(self, funckeys):
        self.validate_types(funckeys)
        keys = {}
        for pos, dest_data in funckeys.iteritems():
            builder = self.destination_builders[dest_data['type']]
            destination = builder.build(dest_data)
            keys[pos] = destination
        return keys

    def validate_types(self, funckeys):
        if not isinstance(funckeys, dict):
            raise errors.wrong_type('keys', 'dict-like structure')

        for pos, dest in funckeys.iteritems():
            if not isinstance(pos, int):
                raise errors.wrong_type('keys', 'numeric positions')
            elif 'type' not in dest:
                raise errors.param_not_found('keys.{}'.format(pos),
                                             'type')
            elif dest['type'] not in self.destination_builders:
                raise errors.invalid_destination_type(dest['type'])


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
