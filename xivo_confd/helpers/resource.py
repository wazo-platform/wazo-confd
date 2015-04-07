# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from flask import request
from flask import url_for

from flask_negotiate import consumes
from flask_negotiate import produces

from xivo_confd.helpers.common import extract_search_parameters
from xivo_confd.helpers.request_bouncer import limit_to_localhost


class CRUDResource(object):

    def __init__(self, service, converter):
        self.service = service
        self.converter = converter

    def search(self):
        search_result = self.service.search(request.args)
        response = self.converter.encode_list(search_result.items, search_result.total)
        return (response, 200, {'Content-Type': 'application/json'})

    def get(self, resource_id):
        resource = self.service.get(resource_id)
        return self.encode_resource(resource)

    def create(self):
        resource = self.converter.decode(request)
        created_resource = self.service.create(resource)
        return self.encode_resource(created_resource, 201)

    def edit(self, resource_id):
        resource = self.service.get(resource_id)
        self.converter.update(request, resource)
        self.service.edit(resource)
        return ('', 204)

    def delete(self, resource_id):
        resource = self.service.get(resource_id)
        self.service.delete(resource)
        return ('', 204)

    def encode_resource(self, resource, status=200):
        response = self.converter.encode(resource)
        location = url_for('.get', resource_id=resource.id)
        return (response, status, {'Location': location,
                                   'Content-Type': 'application/json'})


class CRUDService(object):

    def __init__(self, dao, validator, notifier, extra_parameters=None):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier
        self.extra_parameters = extra_parameters or []

    def search(self, args):
        parameters = extract_search_parameters(args, self.extra_parameters)
        return self.dao.search(**parameters)

    def get(self, resource_id):
        return self.dao.get(resource_id)

    def create(self, resource):
        self.validator.validate_create(resource)
        created_resource = self.dao.create(resource)
        self.notifier.created(created_resource)
        return created_resource

    def edit(self, resource):
        self.validator.validate_edit(resource)
        self.dao.edit(resource)
        self.notifier.edited(resource)

    def delete(self, resource):
        self.validator.validate_delete(resource)
        self.dao.delete(resource)
        self.notifier.deleted(resource)


class DecoratorChain(object):

    @classmethod
    def register_scrud(cls, core, blueprint, resource):
        chain = cls(core, blueprint)
        chain.start().search().decorate(resource.search)
        chain.start().get().decorate(resource.get)
        chain.start().create().decorate(resource.create)
        chain.start().edit().decorate(resource.edit)
        chain.start().delete().decorate(resource.delete)
        core.register(blueprint)

    def __init__(self, core, blueprint):
        self.core = core
        self.blueprint = blueprint
        self.decorators = []

    def start(self):
        self.decorators = []
        return self

    def produce(self):
        self.decorators.append(produces('application/json'))
        return self

    def consume(self):
        self.decorators.append(consumes('application/json'))
        return self

    def authenticate(self):
        self.decorators.append(self.core.auth.login_required)
        return self

    def route_get(self, path):
        decorator = self.blueprint.route(path, methods=['GET'])
        self.decorators.append(decorator)
        return self

    def route_post(self, path):
        decorator = self.blueprint.route(path, methods=['POST'])
        self.decorators.append(decorator)
        return self

    def route_put(self, path):
        decorator = self.blueprint.route(path, methods=['PUT'])
        self.decorators.append(decorator)
        return self

    def route_delete(self, path):
        decorator = self.blueprint.route(path, methods=['DELETE'])
        self.decorators.append(decorator)
        return self

    def limit_localhost(self):
        self.decorators.append(limit_to_localhost)
        return self

    def search(self, path=''):
        return self.produce().authenticate().route_get(path)

    def get(self, path='/<int:resource_id>'):
        return self.produce().authenticate().route_get(path)

    def create(self, path=''):
        return self.consume().produce().authenticate().route_post(path)

    def edit(self, path='/<int:resource_id>'):
        return self.consume().authenticate().route_put(path)

    def delete(self, path='/<int:resource_id>'):
        return self.authenticate().route_delete(path)

    def decorate(self, func):
        for decorator in self.decorators:
            func = decorator(func)
        return func
