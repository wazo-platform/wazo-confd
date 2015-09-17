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

from flask import url_for
from flask_restful import Resource, Api, fields

from xivo_confd.helpers.common import handle_error
from xivo_confd.authentication.confd_auth import ConfdAuth


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


class FieldList(fields.Raw):

    def __init__(self, *links, **kwargs):
        super(FieldList, self).__init__(**kwargs)
        self.links = links

    def output(self, key, obj):
        return [link.output(key, obj) for link in self.links]


class Link(fields.Raw):

    def __init__(self, endpoint, field_name='id', **kwargs):
        super(Link, self).__init__(**kwargs)
        self.endpoint = endpoint
        self.field_name = field_name

    def output(self, key, obj):
        value = getattr(obj, self.field_name)
        options = {self.field_name: value,
                   '_external': True}
        url = url_for(self.endpoint, **options)
        return {'rel': self.endpoint,
                'href': url}
