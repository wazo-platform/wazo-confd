# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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


from marshmallow import fields, post_load
from marshmallow.validate import Length, Range, Predicate, OneOf

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean
from xivo_dao.alchemy.contextnumbers import ContextNumbers


class RangeSchema(BaseSchema):
    start = fields.String(validate=(Predicate('isdigit'), Length(max=16)), required=True)
    end = fields.String(validate=(Predicate('isdigit'), Length(max=16)))


class IncallRangeSchema(RangeSchema):
    did_length = fields.Integer(validate=Range(min=0))


class ContextSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=39), required=True)
    label = fields.String(validate=Length(max=128), allow_none=True)
    type = fields.String(validate=OneOf(['internal', 'incall', 'outcall', 'services', 'others']))
    user_ranges = fields.Nested(RangeSchema, many=True)
    group_ranges = fields.Nested(RangeSchema, many=True)
    queue_ranges = fields.Nested(RangeSchema, many=True)
    conference_room_ranges = fields.Nested(RangeSchema, many=True)
    incall_ranges = fields.Nested(IncallRangeSchema, many=True)
    description = fields.String(allow_none=True)
    enabled = StrictBoolean()
    links = ListLink(Link('contexts'))

    @post_load
    def create_objects(self, data):
        for key in ['user_ranges', 'group_ranges', 'queue_ranges', 'conference_room_ranges', 'incall_ranges']:
            if data.get(key):
                data[key] = [ContextNumbers(**d) for d in data[key]]


class ContextSchemaPUT(ContextSchema):
    name = fields.String(dump_only=True)
