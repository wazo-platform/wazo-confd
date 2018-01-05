# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import url_for
from marshmallow import fields
from marshmallow.validate import OneOf, Regexp

from xivo_dao.alchemy.rightcall import RightCall as CallPermission

from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink
from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource


NAME_REGEX = r'^[a-z0-9_-]{1,128}$'
PASSWORD_REGEX = r'^[0-9#\*]{1,40}$'
EXTENSION_REGEX = r'^(?:_?\+?[0-9NXZ\*#\-\[\]]+[\.\!]?){1,40}$'


class CallPermissionSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Regexp(NAME_REGEX), required=True)
    password = fields.String(validate=Regexp(PASSWORD_REGEX), allow_none=True)
    mode = fields.String(validate=OneOf(['allow', 'deny']))
    extensions = fields.List(fields.String(validate=Regexp(EXTENSION_REGEX)))
    enabled = StrictBoolean()
    description = fields.String(allow_none=True)
    links = ListLink(Link('callpermissions'))

    outcalls = fields.Nested('OutcallSchema',
                             only=['id', 'name', 'links'],
                             many=True,
                             dump_only=True)
    groups = fields.Nested('GroupSchema',
                           only=['id', 'name', 'links'],
                           many=True,
                           dump_only=True)


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
