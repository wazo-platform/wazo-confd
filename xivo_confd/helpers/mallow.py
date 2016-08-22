# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from flask import url_for
from flask_restful import abort
from marshmallow import Schema, fields, pre_load


class BaseSchema(Schema):
    def __init__(self, handle_error=True, *args, **kwargs):
        super(BaseSchema, self).__init__(*args, **kwargs)

        if handle_error:
            def handle_error_fn(error, data):
                return abort(400, message=error.message)

            self.handle_error = handle_error_fn

    def on_bind_field(self, field_name, field_obj):
        # Without this, the nested schema handle error and abort. So the error
        # message will not include parent key and the rest of the parent schema
        # will not be validated
        if isinstance(field_obj, fields.Nested):
            field_obj.schema.handle_error = super(BaseSchema, self).handle_error

    @pre_load
    def ensure_dict(self, data):
        return data or {}


class StrictBoolean(fields.Boolean):

    def _deserialize(self, value, attr, data):
        if not isinstance(value, bool):
            self.fail('invalid')
        return value


class Link(fields.Field):

    _CHECK_ATTRIBUTE = False

    def __init__(self, resource, route=None, field='id', target=None, **kwargs):
        super(Link, self).__init__(dump_only=True, **kwargs)
        self.resource = resource
        self.route = route or resource
        self.field = field
        self.target = target or field

    def _serialize(self, value, key, obj):
        value = self.extract_value(obj)
        if value:
            options = {self.target: value, '_external': True}
            url = url_for(self.route, **options)
            return {'rel': self.resource, 'href': url}

    def extract_value(self, obj):
        if isinstance(obj, dict):
            return obj.get(self.field)
        return getattr(obj, self.field)


class ListLink(fields.Field):

    _CHECK_ATTRIBUTE = False

    def __init__(self, *links, **kwargs):
        super(ListLink, self).__init__(dump_only=True, **kwargs)
        self.links = links

    def _serialize(self, value, key, obj):
        output = []
        for link in self.links:
            link_obj = link.serialize(key, obj)
            if link_obj:
                output.append(link_obj)
        return output
