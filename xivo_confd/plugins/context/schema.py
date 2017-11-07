# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+


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
