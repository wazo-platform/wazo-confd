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

from xivo_dao.data_handler import errors


class Document(object):

    def __init__(self, fields):
        self.fields = fields

    def validate(self, content, action=None):
        self._validate_unknown_fields(content)
        self._validate_fields(content, action)

    def _validate_unknown_fields(self, content):
        fields = content.keys()
        valid_fields = self.field_names()
        invalid_fields = set(fields) - set(valid_fields)
        if invalid_fields:
            raise errors.unknown(*invalid_fields)

    def _validate_fields(self, content, action):
        for field in self.fields:
            value = content.get(field.name)
            field.validate(value, action)

    def field_names(self):
        return tuple(f.name for f in self.fields)


class DocumentProxy(object):

    def __init__(self, parser, document):
        self.parser = parser
        self.document = document

    def parse(self, request, action=None):
        return self.parser.parse(request, self.document, action)

    def validate(self, content, action=None):
        return self.document.validate(content, action)

    def field_names(self):
        return self.document.field_names()
