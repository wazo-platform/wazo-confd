# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from flask_restful import reqparse, fields, marshal

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import Strict, ConfdResource
from xivo_dao.helpers import errors


class UserSubResource(ConfdResource):

    def __init__(self, service):
        self.service = service

    def get_user(self, user_id):
        if isinstance(user_id, int):
            return self.service.get(user_id)
        return self.service.get_by(uuid=str(user_id))

    def parse_and_update(self, model, parser_name):
        form = self.parsers[parser_name].parse_args()
        for name, value in form.iteritems():
            setattr(model, name, value)
        self.service.edit(model, parser_name)


service_fields = {
    'dnd': {
        'enabled': fields.Boolean(attribute='dnd_enabled'),
    },
    'incallfilter': {
        'enabled': fields.Boolean(attribute='incallfilter_enabled'),
    }
}

service_parsers = {
    'dnd':
        (reqparse.RequestParser()
            .add_argument('enabled', type=Strict(bool), store_missing=False, required=True, nullable=False,
                          dest='dnd_enabled')),
    'incallfilter':
        (reqparse.RequestParser()
            .add_argument('enabled', type=Strict(bool), store_missing=False, required=True, nullable=False,
                          dest='incallfilter_enabled')),
}


class UserServiceItem(UserSubResource):

    fields = service_fields
    parsers = service_parsers

    def validate_service(self, service_name):
        if service_name not in self.fields:
            raise errors.not_found('Service', service=service_name)

    @required_acl('confd.users.{user_id}.services.{service_name}.read')
    def get(self, user_id, service_name):
        self.validate_service(service_name)
        user = self.get_user(user_id)
        return marshal(user, self.fields[service_name])

    @required_acl('confd.users.{user_id}.services.{service_name}.update')
    def put(self, user_id, service_name):
        self.validate_service(service_name)
        user = self.get_user(user_id)
        self.parse_and_update(user, service_name)
        return '', 204


class UserServiceList(UserSubResource):

    fields = service_fields

    @required_acl('confd.users.{user_id}.services.read')
    def get(self, user_id):
        user = self.get_user(user_id)
        return marshal(user, self.fields)


forward_fields = {
    'busy': {
        'enabled': fields.Boolean(attribute='busy_enabled'),
        'destination': fields.String(attribute='busy_destination')
    },
    'noanswer': {
        'enabled': fields.Boolean(attribute='noanswer_enabled'),
        'destination': fields.String(attribute='noanswer_destination')
    },
    'unconditional': {
        'enabled': fields.Boolean(attribute='unconditional_enabled'),
        'destination': fields.String(attribute='unconditional_destination')
    }
}

forward_parsers = {
    'busy':
        (reqparse.RequestParser()
            .add_argument('enabled', type=Strict(bool), store_missing=False, nullable=False,
                          dest='busy_enabled')
            .add_argument('destination', type=Strict(unicode), store_missing=False,
                          dest='busy_destination')),
    'noanswer':
        (reqparse.RequestParser()
            .add_argument('enabled', type=Strict(bool), store_missing=False, nullable=False,
                          dest='noanswer_enabled')
            .add_argument('destination', type=Strict(unicode), store_missing=False,
                          dest='noanswer_destination')),
    'unconditional':
        (reqparse.RequestParser()
            .add_argument('enabled', type=Strict(bool), store_missing=False, nullable=False,
                          dest='unconditional_enabled')
            .add_argument('destination', type=Strict(unicode), store_missing=False,
                          dest='unconditional_destination'))
}


class UserForwardItem(UserSubResource):

    fields = forward_fields
    parsers = forward_parsers

    def validate_forward(self, forward_name):
        if forward_name not in self.fields:
            raise errors.not_found('Forward', forward=forward_name)

    @required_acl('confd.users.{user_id}.forwards.{forward_name}.read')
    def get(self, user_id, forward_name):
        self.validate_forward(forward_name)
        user = self.get_user(user_id)
        return marshal(user, self.fields[forward_name])

    @required_acl('confd.users.{user_id}.forwards.{forward_name}.update')
    def put(self, user_id, forward_name):
        self.validate_forward(forward_name)
        user = self.get_user(user_id)
        self.parse_and_update(user, forward_name)
        return '', 204


class UserForwardList(UserSubResource):

    fields = forward_fields

    @required_acl('confd.users.{user_id}.forwards.read')
    def get(self, user_id):
        user = self.get_user(user_id)
        return marshal(user, self.fields)
