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

from flask import url_for

from marshmallow import fields
from marshmallow.validate import OneOf, Regexp

from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink
from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource
from xivo_dao.alchemy.rightcall import RightCall as CallPermission


NAME_REGEX = r'^[a-z0-9_-]{1,128}$'
PASSWORD_REGEX = r'^[0-9#\*]{1,40}$'
EXTENSION_REGEX = r'^(?:_?\+?[0-9NXZ\*#\-\[\]]+[\.\!]?){1,40}$'


class CallPermissionSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Regexp(NAME_REGEX))
    password = fields.String(validate=Regexp(PASSWORD_REGEX), allow_none=True)
    mode = fields.String(validate=OneOf(['allow', 'deny']))
    extensions = fields.List(fields.String(validate=Regexp(EXTENSION_REGEX)))
    enabled = StrictBoolean()
    description = fields.String(allow_none=True)
    links = ListLink(Link('callpermissions'))


class CallPermissionList(ListResource):

    model = CallPermission
    schema = CallPermissionSchema

    def build_headers(self, call_permission):
        return {'Location': url_for('callpermissions', id=call_permission.id, _external=True)}

    @required_acl('confd.callpermissions.create')
    def post(self):
        return super(CallPermissionList, self).post()

    @required_acl('confd.callpermissions.read')
    def get(self):
        return super(CallPermissionList, self).get()


class CallPermissionItem(ItemResource):

    schema = CallPermissionSchema

    @required_acl('confd.callpermissions.{id}.read')
    def get(self, id):
        return super(CallPermissionItem, self).get(id)

    @required_acl('confd.callpermissions.{id}.update')
    def put(self, id):
        return super(CallPermissionItem, self).put(id)

    @required_acl('confd.callpermissions.{id}.delete')
    def delete(self, id):
        return super(CallPermissionItem, self).delete(id)
