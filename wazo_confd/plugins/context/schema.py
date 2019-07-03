# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length, Range, Predicate, OneOf

from xivo_dao.alchemy.contextnumbers import ContextNumbers

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean


class RangeSchema(BaseSchema):
    start = fields.String(validate=(Predicate('isdigit'), Length(max=16)), required=True)
    end = fields.String(validate=(Predicate('isdigit'), Length(max=16)))

    def validate_range(self, start, end):
        if start > end:
            raise ValidationError('Start of range must be lower than or equal to the end')

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if data.get('start') and data.get('end'):
            self.validate_range(int(data['start']), int(data['end']))


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
    tenant_uuid = fields.String(dump_only=True)
    enabled = StrictBoolean()
    links = ListLink(Link('contexts'))

    contexts = fields.Nested(
        'ContextSchema',
        only=['id', 'name', 'label', 'links'],
        many=True,
        dump_only=True,
    )

    @post_load
    def create_objects(self, data):
        for key in ['user_ranges', 'group_ranges', 'queue_ranges', 'conference_room_ranges', 'incall_ranges']:
            if data.get(key):
                data[key] = [ContextNumbers(**d) for d in data[key]]


class ContextSchemaPUT(ContextSchema):
    name = fields.String(dump_only=True)
