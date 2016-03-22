# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from datetime import datetime
from flask import url_for, request
from flask_restful import Resource, Api, fields, marshal

from xivo_confd.helpers.common import handle_error
from xivo_confd.authentication.confd_auth import auth

from xivo_dao.helpers import errors


def option(option):
    if not isinstance(option, list):
        raise ValueError("item '{}' must be a pair of strings".format(option))
    if len(option) != 2:
        raise ValueError("item '{}' must be a pair of strings".format(option))
    for i in option:
        if not isinstance(i, (str, unicode)):
            raise ValueError("value '{}' is not a string".format(i))
    return option


class Strict(object):

    def __init__(self, typecast):
        self.typecast = typecast

    def __call__(self, value):
        if not isinstance(value, self.typecast):
            name = self.typecast.__name__
            raise ValueError("value '{}' must be a {}".format(value, name))
        return value


class DigitStr(object):

    def __init__(self, length=None):
        self.length = length

    def __call__(self, value):
        if not value.isdigit():
            raise ValueError("'{}' is not a string of digits".format(value))
        if self.length and len(value) != self.length:
            raise ValueError("'{}' must have a length of {}".format(value, self.length))
        return value


class DateTimeLocalZone(object):

    def __call__(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            raise ValueError("'{}' must be of the form '2016-12-23T04:05:06'".format(value))


class ConfdApi(Api):

    def handle_error(self, error):
        try:
            return handle_error(error)
        except:
            return super(self, ConfdApi).handle_error(error)


class ConfdResource(Resource):
    method_decorators = [auth.login_required]


class ListResource(ConfdResource):

    def __init__(self, service):
        super(ListResource, self).__init__()
        self.service = service

    def get(self):
        params = self.search_params()
        total, items = self.service.search(params)
        return {'total': total,
                'items': [marshal(item, self.fields) for item in items]}

    def search_params(self):
        args = ((key, request.args[key]) for key in request.args)
        params = {}

        for key, value in args:
            if key in ("limit", "skip", "offset"):
                params[key] = self.convert_numeric(key, value)
            else:
                params[key] = value

        return params

    def convert_numeric(self, key, value):
        if not value.isdigit():
            raise errors.wrong_type(key, "positive number")
        return int(value)

    def post(self):
        form = self.parser.parse_args()
        model = self.model(**form)
        model = self.service.create(model)
        return marshal(model, self.fields), 201, self.build_headers(model)

    def build_headers(self, model):
        raise NotImplementedError()


class ItemResource(ConfdResource):

    def __init__(self, service):
        super(ItemResource, self).__init__()
        self.service = service

    def get(self, id):
        model = self.service.get(id)
        return marshal(model, self.fields)

    def put(self, id):
        model = self.service.get(id)
        self.parse_and_update(model)
        return '', 204

    def parse_and_update(self, model):
        form = self.parser.parse_args()
        for name, value in form.iteritems():
            setattr(model, name, value)
        self.service.edit(model)

    def delete(self, id):
        model = self.service.get(id)
        self.service.delete(model)
        return '', 204


class FieldList(fields.Raw):

    def __init__(self, *links, **kwargs):
        super(FieldList, self).__init__(**kwargs)
        self.links = links

    def output(self, key, obj):
        fields = []
        for link in self.links:
            output = link.output(key, obj)
            if output:
                fields.append(output)
        return fields


class Link(fields.Raw):

    def __init__(self, resource, route=None, field='id', target=None, **kwargs):
        super(Link, self).__init__(**kwargs)
        self.resource = resource
        self.route = route or resource
        self.field = field
        self.target = target or field

    def output(self, key, obj):
        value = self.extract_value(obj)
        if value:
            options = {self.target: value, '_external': True}
            url = url_for(self.route, **options)
            return {'rel': self.resource, 'href': url}

    def extract_value(self, obj):
        if isinstance(obj, dict):
            return obj.get(self.field)
        return getattr(obj, self.field)
