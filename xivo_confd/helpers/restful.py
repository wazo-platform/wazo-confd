# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from flask import url_for, request
from flask_restful import Resource, Api, fields, marshal

from xivo_confd.helpers.common import handle_error
from xivo_confd.authentication.confd_auth import ConfdAuth


def option(option):
    if not isinstance(option, list):
        raise ValueError("item '{}' must be a pair of strings".format(option))
    if len(option) != 2:
        raise ValueError("item '{}' must be a pair of strings".format(option))
    for i in option:
        if not isinstance(i, (str, unicode)):
            raise ValueError("value '{}' is not a string".format(i))
    return option


class DigitStr(object):

    def __init__(self, length=None):
        self.length = length

    def __call__(self, value):
        if not value.isdigit():
            raise ValueError("'{}' is not a string of digits".format(value))
        if self.length and len(value) != self.length:
            raise ValueError("'{}' must have a length of {}".format(value, self.length))
        return value


class ConfdApi(Api):

    def handle_error(self, error):
        try:
            return handle_error(error)
        except:
            return super(self, ConfdApi).handle_error(error)


class ConfdResource(Resource):
    method_decorators = [ConfdAuth().login_required]


class ListResource(ConfdResource):

    def __init__(self, service):
        super(ListResource, self).__init__()
        self.service = service

    def get(self):
        params = {key: request.args[key] for key in request.args}
        total, items = self.service.search(params)
        return {'total': total,
                'items': [marshal(item, self.fields) for item in items]}

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
        form = self.parser.parse_args()
        for name, value in form.iteritems():
            setattr(model, name, value)
        self.service.edit(model)
        return '', 204

    def delete(self, id):
        model = self.service.get(id)
        self.service.delete(model)
        return '', 204


class FieldList(fields.Raw):

    def __init__(self, *links, **kwargs):
        super(FieldList, self).__init__(**kwargs)
        self.links = links

    def output(self, key, obj):
        return [link.output(key, obj) for link in self.links]


class Link(fields.Raw):

    def __init__(self, resource, route=None, field='id', target=None, **kwargs):
        super(Link, self).__init__(**kwargs)
        self.resource = resource
        self.route = route or resource
        self.field = field
        self.target = target or field

    def output(self, key, obj):
        if isinstance(obj, dict):
            value = obj.get(self.field)
        else:
            value = getattr(obj, self.field)
        options = {self.target: value, '_external': True}
        url = url_for(self.route, **options)
        return {'rel': self.resource, 'href': url}
