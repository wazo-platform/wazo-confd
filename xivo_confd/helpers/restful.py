# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from flask import request
from flask_restful import Resource, Api

from xivo_confd.helpers.common import handle_error
from xivo_confd.authentication.confd_auth import auth

from xivo_dao.helpers import errors


class ConfdApi(Api):

    def handle_error(self, error):
        try:
            return handle_error(error)
        except:
            return super(ConfdApi, self).handle_error(error)


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
                'items': self.schema().dump(items, many=True).data}

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
        form = self.schema().load(request.get_json()).data
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model).data, 201, self.build_headers(model)

    def build_headers(self, model):
        raise NotImplementedError()


class ItemResource(ConfdResource):

    def __init__(self, service):
        super(ItemResource, self).__init__()
        self.service = service

    def get(self, id):
        model = self.service.get(id)
        return self.schema().dump(model).data

    def put(self, id):
        model = self.service.get(id)
        self.parse_and_update(model)
        return '', 204

    def parse_and_update(self, model):
        form = self.schema().load(request.get_json(), partial=True).data
        updated_fields = self.find_updated_fields(model, form)
        for name, value in form.iteritems():
            setattr(model, name, value)
        self.service.edit(model, updated_fields)

    def find_updated_fields(self, model, form):
        updated_fields = []
        for name, value in form.iteritems():
            try:
                if getattr(model, name) != value:
                    updated_fields.append(name)
            except AttributeError:
                pass
        return updated_fields

    def delete(self, id):
        model = self.service.get(id)
        self.service.delete(model)
        return '', 204
