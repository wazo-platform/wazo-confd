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

import abc
import json

from flask import helpers


class Mapper(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def for_encoding(self, mapping):
        return

    @abc.abstractmethod
    def for_decoding(self, mapping):
        return


class Serializer(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def serialize(self, data):
        return

    @abc.abstractmethod
    def serialize_list(self, items, total=None):
        return


class Parser(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parse(self, request):
        return


class DocumentMapper(Mapper):

    def __init__(self, document):
        self.document = document

    def for_encoding(self, model):
        return {name: getattr(model, name) for name in self.document.field_names()}

    def for_decoding(self, mapping):
        return {name: mapping[name]
                for name in self.document.field_names()
                if name in mapping}


class DocumentParser(Parser):

    def __init__(self, document):
        self.document = document

    def parse(self, request):
        return self.document.parse(request)


class AssociationParser(Parser):

    def __init__(self, document):
        self.document = document

    def parse(self, request):
        mapping = self.document.parse(request)
        mapping.update({name: request.view_args[name]
                        for name in self.document.field_names()
                        if name in request.view_args})
        self.document.validate(mapping)
        return mapping


class JsonSerializer(Serializer):

    def __init__(self, resources):
        self.resources = resources

    def serialize(self, mapping):
        mapping = self._map_item(mapping)
        return json.dumps(mapping)

    def _map_item(self, mapping):
        mapping['links'] = [self._generate_link(resource, mapping[resource_id])
                            for resource, resource_id in self.resources.iteritems()]
        return mapping

    def _generate_link(self, resource, resource_id):
        return {'rel': resource,
                'href': helpers.url_for(resource + '.get',
                                        resource_id=resource_id,
                                        _external=True)}

    def serialize_list(self, items, total=None):
        result = {'total': total or len(items),
                  'items': [self._map_item(item) for item in items]}
        return json.dumps(result)


class Converter(object):

    def __init__(self, model, parser, mapper, serializer):
        self.model = model
        self.parser = parser
        self.mapper = mapper
        self.serializer = serializer

    def encode(self, model):
        mapped_model = self.mapper.for_encoding(model)
        return self.serializer.serialize(mapped_model)

    def encode_list(self, items, total=None):
        mapped_items = [self.mapper.for_encoding(item) for item in items]
        return self.serializer.serialize_list(mapped_items, total=total)

    def decode(self, request):
        parsed_request = self.parser.parse(request)
        mapped_request = self.mapper.for_decoding(parsed_request)
        return self.model(**mapped_request)

    def update(self, request, model):
        parsed_mapping = self.parser.parse(request)
        mapped_model = self.mapper.for_decoding(parsed_mapping)
        for name, value in mapped_model.iteritems():
            setattr(model, name, value)

    @classmethod
    def for_document(cls, document, model, resource_name=None, resource_id=None):
        parser = DocumentParser(document)
        mapper = DocumentMapper(document)
        resource_name = resource_name or model.__name__.lower() + 's'
        resource_id = resource_id or 'id'
        serializer = JsonSerializer({resource_name: resource_id})
        return cls(model, parser, mapper, serializer)

    @classmethod
    def for_association(cls, document, model, links):
        parser = AssociationParser(document)
        mapper = DocumentMapper(document)
        serializer = JsonSerializer(links)
        return cls(model, parser, mapper, serializer)
