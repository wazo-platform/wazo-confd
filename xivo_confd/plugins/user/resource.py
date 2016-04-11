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
from xivo_confd.helpers.restful import FieldList, Link, ListResource, ItemResource, Strict
from xivo_dao.alchemy.userfeatures import UserFeatures as User


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

view_fields = {
    'directory': {
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
    },
    'summary': {
        'id': fields.Integer,
        'uuid': fields.String,
        'firstname': fields.String,
        'lastname': fields.String,
        'extension': fields.String,
        'context': fields.String,
        'provisioning_code': fields.String,
        'entity': fields.String,
        'protocol': fields.String,
        'enabled': fields.Boolean,
    }
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
parser.add_argument('caller_id', type=Strict(unicode), store_missing=False)
parser.add_argument('mobile_phone_number', type=Strict(unicode), store_missing=False)


class UserList(ListResource):

    model = User
    fields = user_fields
    parser = parser

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
        view = request.args.get('view')
        fields = view_fields.get(view, user_fields)
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
