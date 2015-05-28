# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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


class Builder(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create(self, mapping):
        return

    @abc.abstractmethod
    def update(self, model, mapping):
        return


class DocumentMapper(Mapper):

    def __init__(self, document, rename=None):
        self.document = document
        self.rename = rename or {}

    def for_encoding(self, model):
        return {name: getattr(model, name) for name in self.document.field_names()}

    def for_decoding(self, mapping):
        return self.adjust_mapping(mapping)

    def adjust_mapping(self, mapping):
        renamed_mapping = self.rename_mapping(mapping)
        return self.extract_mapping(renamed_mapping)

    def rename_mapping(self, mapping):
        for old_name, new_name in self.rename.items():
            if old_name in mapping:
                mapping[new_name] = mapping.pop(old_name)
        return mapping

    def extract_mapping(self, mapping):
        return {name: mapping[name]
                for name in self.document.field_names()
                if name in mapping}


class DocumentParser(Parser):

    def __init__(self, document):
        self.document = document

    def parse(self, request):
        return self.document.parse(request)


class RequestParser(Parser):

    def __init__(self, document, extra=None):
        self.document = document
        self.extra = tuple(extra) if extra else tuple()

    def parse(self, request):
        mapping = self.document.parse(request)
        field_names = self.document.field_names() + self.extra
        mapping.update({name: request.view_args[name]
                        for name in field_names
                        if name in request.view_args})
        return mapping


class ResourceSerializer(Serializer):

    def __init__(self, resources):
        self.resources = resources

    def serialize(self, mapping):
        mapping = self._map_item(mapping)
        return json.dumps(mapping)

    def _map_item(self, mapping):
        mapping['links'] = [self._generate_link(resource, mapping[resource_id])
                            for resource, resource_id in self.resources.iteritems()
                            if mapping.get(resource_id) is not None]
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


class ModelBuilder(Builder):

    def __init__(self, document, model_class):
        self.document = document
        self.model_class = model_class

    def create(self, mapping):
        self.document.validate(mapping)
        return self.model_class(**mapping)

    def update(self, model, mapping):
        self.document.validate(mapping)
        for attr_name, attr_value in mapping.iteritems():
            setattr(model, attr_name, attr_value)


class Converter(object):

    def __init__(self, parser, mapper, serializer, builder):
        self.parser = parser
        self.mapper = mapper
        self.serializer = serializer
        self.builder = builder

    def encode(self, model):
        mapped_model = self.mapper.for_encoding(model)
        return self.serializer.serialize(mapped_model)

    def encode_list(self, items, total=None):
        mapped_items = [self.mapper.for_encoding(item) for item in items]
        return self.serializer.serialize_list(mapped_items, total=total)

    def decode(self, request):
        parsed_request = self.parser.parse(request)
        mapped_request = self.mapper.for_decoding(parsed_request)
        return self.builder.create(mapped_request)

    def update(self, request, model):
        parsed_request = self.parser.parse(request)
        parsed_mapping = self.mapper.for_decoding(parsed_request)
        self.builder.update(model, parsed_mapping)

    @classmethod
    def association(cls, document, model, links=None, rename=None):
        links = links or {}
        rename = rename or {}
        parser = RequestParser(document, rename.keys())
        mapper = DocumentMapper(document, rename)
        serializer = ResourceSerializer(links)
        builder = ModelBuilder(document, model)
        return cls(parser, mapper, serializer, builder)

    @classmethod
    def resource(cls, document, model, resource_name=None, resource_id=None):
        resource_name = resource_name or model.__name__.lower() + 's'
        resource_id = resource_id or 'id'
        links = {resource_name: resource_id}

        parser = DocumentParser(document)
        mapper = DocumentMapper(document)
        serializer = ResourceSerializer(links)
        builder = ModelBuilder(document, model)
        return cls(parser, mapper, serializer, builder)
