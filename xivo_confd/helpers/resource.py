# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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


def build_response(response, code=200, location=None):
    headers = {'Content-Type': 'application/json'}
    if location:
        headers['Location'] = location
    return (response, code, headers)


class CRUDResource(object):

    def __init__(self, service, converter, extra_parameters=None):
        self.service = service
        self.converter = converter
        self.extra_parameters = extra_parameters

    def search(self):
        parameters = extract_search_parameters(request.args, self.extra_parameters)
        search_result = self.service.search(parameters)
        response = self.converter.encode_list(search_result.items, search_result.total)
        return build_response(response)

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
        return build_response(response, status, location)


class CollectionAssociationResource(object):

    def __init__(self, service, converter):
        self.service = service
        self.converter = converter

    def list_association(self, parent_id):
        associations = self.service.list(parent_id)
        response = self.converter.encode_list(associations)
        return build_response(response)

    def associate_collection(self, parent_id):
        association = self.converter.decode(request)
        created_association = self.service.associate(association)
        response = self.converter.encode(created_association)
        location = url_for('.list_association', parent_id=parent_id)
        return build_response(response, 201, location)

    def dissociate_collection(self, parent_id, resource_id):
        association = self.service.get(parent_id, resource_id)
        self.service.dissociate(association)
        return ('', 204)


class SingleAssociationResource(object):

    def __init__(self, service, converter):
        self.service = service
        self.converter = converter

    def get_association(self, parent_id):
        association = self.service.get_by_parent(parent_id)
        response = self.converter.encode(association)
        return build_response(response)

    def associate(self, parent_id):
        association = self.converter.decode(request)
        created_association = self.service.associate(association)
        response = self.converter.encode(created_association)
        location = url_for('.get_association', parent_id=parent_id)
        return build_response(response, 201, location)

    def dissociate(self, parent_id):
        association = self.service.get_by_parent(parent_id)
        self.service.dissociate(association)
        return ('', 204)


class CRUDService(object):

    def __init__(self, dao, validator, notifier, extra_parameters=None):
        self.dao = dao
        self.validator = validator
        self.notifier = notifier
        self.extra_parameters = extra_parameters or []

    def search(self, parameters):
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
        chain.search().decorate(resource.search)
        chain.get().decorate(resource.get)
        chain.create().decorate(resource.create)
        chain.edit().decorate(resource.edit)
        chain.delete().decorate(resource.delete)
        core.register(blueprint)

    def __init__(self, core, blueprint):
        self.core = core
        self.blueprint = blueprint
        self.decorators = []

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
        self.decorators = []
        return func
