# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
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

from marshmallow import fields, post_dump
from marshmallow.validate import Length, Predicate

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class PagingSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    number = fields.String(validate=(Length(max=32), Predicate('isdigit')), required=True)
    name = fields.String(validate=Length(max=128), allow_none=True)
    announce_caller = fields.Boolean()
    announce_sound = fields.String(validate=Length(max=64), allow_none=True)
    caller_notification = fields.Boolean()
    duplex = fields.Boolean(attribute='duplex_bool')
    ignore_forward = fields.Boolean()
    record = fields.Boolean(attribute='record_bool')
    enabled = fields.Boolean()
    links = ListLink(Link('pagings'))

    users_caller = fields.Nested('UserSchema',
                                 only=['uuid', 'firstname', 'lastname', 'links'],
                                 many=True,
                                 dummp_only=True)
    users_member = fields.Nested('UserSchema',
                                 only=['uuid', 'firstname', 'lastname', 'links'],
                                 many=True,
                                 dummp_only=True)

    @post_dump
    def wrap_users(self, data):
        data['callers'] = {'users': data.pop('users_caller', [])}
        data['members'] = {'users': data.pop('users_member', [])}
        return data
