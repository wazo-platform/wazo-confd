# -*- coding: utf-8 -*-

# Copyright (C) 2016 Francois Blackburn
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

from marshmallow import fields
from marshmallow.validate import Length, Predicate, Range

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class ConferenceSchema(BaseSchema):
    id = fields.Integer()
    name = fields.String(allow_none=True, validate=Length(max=128))
    preprocess_subroutine = fields.String(allow_none=True, validate=Length(max=39))
    max_users = fields.Integer(validate=Range(min=0))
    record = fields.Boolean()
    pin = fields.String(validate=(Length(max=80), Predicate('isdigit')))
    admin_pin = fields.String(validate=(Length(max=80), Predicate('isdigit')))
    notify_join_leave = fields.Boolean()
    announce_join_leave = fields.Boolean()
    announce_user_count = fields.Boolean()
    announce_only_user = fields.Boolean()
    music_on_hold = fields.String(allow_none=True, validate=Length(max=128))
    links = ListLink(Link('conferences'))

    extensions = fields.Nested('ExtensionSchema',
                               only=['id', 'exten', 'context', 'links'],
                               many=True,
                               dump_only=True)
