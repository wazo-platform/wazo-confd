# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from flask import url_for, request
from flask_restful import reqparse, fields, marshal

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import FieldList, Link, ListResource, ItemResource, Strict, ConfdResource
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.helpers import errors


user_fields = {
    'id': fields.Integer,
    'uuid': fields.String,
    'firstname': fields.String,
    'lastname': fields.String,
    'email': fields.String,
    'timezone': fields.String,
    'language': fields.String,
    'description': fields.String,
    'caller_id': fields.String,
    'outgoing_caller_id': fields.String,
    'mobile_phone_number': fields.String,
    'username': fields.String,
    'password': fields.String,
    'music_on_hold': fields.String,
    'preprocess_subroutine': fields.String,
    'userfield': fields.String,
    'call_transfer_enabled': fields.Boolean,
    'call_record_enabled': fields.Boolean,
    'online_call_record_enabled': fields.Boolean,
    'supervision_enabled': fields.Boolean,
    'ring_seconds': fields.Integer,
    'simultaneous_calls': fields.Integer,
    'links': FieldList(Link('users'))
}

directory_fields = {
    'id': fields.Integer,
    'uuid': fields.String,
    'line_id': fields.Integer(default=None),
    'agent_id': fields.Integer(default=None),
    'firstname': fields.String,
    'lastname': fields.String,
    'email': fields.String,
    'exten': fields.String,
    'mobile_phone_number': fields.String,
    'voicemail_number': fields.String,
    'userfield': fields.String,
    'description': fields.String,
    'context': fields.String,
}

parser = reqparse.RequestParser()
parser.add_argument('firstname', type=Strict(unicode), store_missing=False, nullable=False)
parser.add_argument('lastname', type=Strict(unicode), store_missing=False)
parser.add_argument('email', type=Strict(unicode), store_missing=False)
parser.add_argument('timezone', type=Strict(unicode), store_missing=False)
parser.add_argument('language', type=Strict(unicode), store_missing=False)
parser.add_argument('description', type=Strict(unicode), store_missing=False)
parser.add_argument('outgoing_caller_id', type=Strict(unicode), store_missing=False)
parser.add_argument('username', type=Strict(unicode), store_missing=False)
parser.add_argument('password', type=Strict(unicode), store_missing=False)
parser.add_argument('music_on_hold', type=Strict(unicode), store_missing=False)
parser.add_argument('preprocess_subroutine', type=Strict(unicode), store_missing=False)
parser.add_argument('userfield', type=Strict(unicode), store_missing=False)
parser.add_argument('call_transfer_enabled', type=Strict(bool), store_missing=False)
parser.add_argument('call_record_enabled', type=Strict(bool), store_missing=False)
parser.add_argument('online_call_record_enabled', type=Strict(bool), store_missing=False)
parser.add_argument('supervision_enabled', type=Strict(bool), store_missing=False)
parser.add_argument('ring_seconds', type=int, store_missing=False)
parser.add_argument('simultaneous_calls', type=int, store_missing=False)
parser.add_argument('caller_id', store_missing=False, type=Strict(unicode))
parser.add_argument('mobile_phone_number', store_missing=False, type=Strict(unicode))


class UserList(ListResource):

    model = User
    fields = user_fields

    parser = reqparse.RequestParser()
    parser.add_argument('firstname', type=Strict(unicode), required=True)
    parser.add_argument('lastname', type=Strict(unicode))
    parser.add_argument('email', type=Strict(unicode))
    parser.add_argument('timezone', type=Strict(unicode))
    parser.add_argument('language', type=Strict(unicode))
    parser.add_argument('description', type=Strict(unicode))
    parser.add_argument('outgoing_caller_id', type=Strict(unicode))
    parser.add_argument('username', type=Strict(unicode))
    parser.add_argument('password', type=Strict(unicode))
    parser.add_argument('music_on_hold', type=Strict(unicode))
    parser.add_argument('preprocess_subroutine', type=Strict(unicode))
    parser.add_argument('userfield', type=Strict(unicode))
    parser.add_argument('caller_id', type=Strict(unicode))
    parser.add_argument('mobile_phone_number', type=Strict(unicode))
    parser.add_argument('call_transfer_enabled', type=Strict(bool))
    parser.add_argument('call_record_enabled', type=Strict(bool))
    parser.add_argument('online_call_record_enabled', type=Strict(bool))
    parser.add_argument('supervision_enabled', type=Strict(bool))
    parser.add_argument('ring_seconds', type=int)
    parser.add_argument('simultaneous_calls', type=int)

    def build_headers(self, user):
        return {'Location': url_for('users', id=user.id, _external=True)}

    @required_acl('confd.users.create')
    def post(self):
        return super(UserList, self).post()

    @required_acl('confd.users.read')
    def get(self):
        if 'q' in request.args:
            return self.legacy_search()
        else:
            return self.user_search()

    def legacy_search(self):
        result = self.service.legacy_search(request.args['q'])
        return {'total': result.total,
                'items': [marshal(item, user_fields) for item in result.items]}

    def user_search(self):
        if request.args.get('view') == 'directory':
            fields = directory_fields
        else:
            fields = user_fields

        params = self.search_params()
        result = self.service.search(params)

        return {'total': result.total,
                'items': [marshal(item, fields) for item in result.items]}


class UserItem(ItemResource):

    fields = user_fields
    parser = parser

    @required_acl('confd.users.{id}.read')
    def get(self, id):
        return super(UserItem, self).get(id)

    @required_acl('confd.users.{id}.update')
    def put(self, id):
        return super(UserItem, self).put(id)

    @required_acl('confd.users.{id}.delete')
    def delete(self, id):
        return super(UserItem, self).delete(id)


class UserUuidItem(ItemResource):

    fields = user_fields
    parser = parser

    @required_acl('confd.users.{uuid}.read')
    def get(self, uuid):
        user = self.service.get_by(uuid=str(uuid))
        return marshal(user, self.fields)

    @required_acl('confd.users.{uuid}.update')
    def put(self, uuid):
        user = self.service.get_by(uuid=str(uuid))
        self.parse_and_update(user)
        return '', 204

    @required_acl('confd.users.{uuid}.delete')
    def delete(self, uuid):
        user = self.service.get_by(uuid=str(uuid))
        self.service.delete(user)
        return '', 204


service_fields = {
    'dnd': {
        'enabled': fields.Boolean(attribute='dnd_enabled'),
    },
    'incallfilter': {
        'enabled': fields.Boolean(attribute='incallfilter_enabled'),
    }
}

service_parser = reqparse.RequestParser()
service_parser.add_argument('enabled', type=Strict(bool), store_missing=False, required=True, nullable=False)


class UserServiceItem(ConfdResource):

    fields = service_fields
    parser = service_parser

    def __init__(self, service, user_dao):
        self.service = service
        self.user_dao = user_dao

    def get_user(self, user_id):
        if isinstance(user_id, int):
            return self.user_dao.get(user_id)
        return self.user_dao.get_by(uuid=str(user_id))

    @required_acl('confd.users.{user_id}.services.{service_name}.read')
    def get(self, user_id, service_name):
        if service_name not in service_fields:
            raise errors.not_found('Service', service=service_name)

        user = self.get_user(user_id)
        return marshal(user, self.fields[service_name])

    @required_acl('confd.users.{user_id}.services.{service_name}.update')
    def put(self, user_id, service_name):
        user = self.get_user(user_id)
        setattr(user, service_fields[service_name]['enabled'].attribute, self.parser.parse_args()['enabled'])
        self.service.edit(user)
        return '', 204


class UserServiceList(ConfdResource):

    fields = service_fields

    def __init__(self, service, user_dao):
        self.service = service
        self.user_dao = user_dao

    def get_user(self, user_id):
        if isinstance(user_id, int):
            return self.user_dao.get(user_id)
        return self.user_dao.get_by(uuid=str(user_id))

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

forward_parser = reqparse.RequestParser()
forward_parser.add_argument('enabled', type=Strict(bool), store_missing=False, nullable=False)
forward_parser.add_argument('destination', type=Strict(unicode), store_missing=False, nullable=False)


class UserForwardItem(ConfdResource):

    fields = forward_fields
    parser = forward_parser

    def __init__(self, service, user_dao):
        self.service = service
        self.user_dao = user_dao

    def get_user(self, user_id):
        if isinstance(user_id, int):
            return self.user_dao.get(user_id)
        return self.user_dao.get_by(uuid=str(user_id))

    def validate_forward(self, forward_name):
        if forward_name not in self.fields:
            raise errors.not_found('Forward', forward=forward_name)

    def parse_and_update(self, model, forward_name):
        form = self.parser.parse_args()
        for name, value in form.iteritems():
            setattr(model, self.fields[forward_name][name].attribute, value)
        self.service.edit(model)

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


class UserForwardList(ConfdResource):

    fields = forward_fields

    def __init__(self, service, user_dao):
        self.service = service
        self.user_dao = user_dao

    def get_user(self, user_id):
        if isinstance(user_id, int):
            return self.user_dao.get(user_id)
        return self.user_dao.get_by(uuid=str(user_id))

    @required_acl('confd.users.{user_id}.forwards.read')
    def get(self, user_id):
        user = self.get_user(user_id)
        return marshal(user, self.fields)
