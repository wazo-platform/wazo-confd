# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import (
    Length,
    NoneOf,
    OneOf,
    Predicate,
    Range,
    Regexp,
)

from xivo_dao.alchemy.contextnumbers import ContextNumbers

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean

CONTEXT_REGEX = r"^[a-zA-Z0-9-_]*$"


class RangeSchema(BaseSchema):
    start = fields.String(validate=(Predicate('isdigit'), Length(max=16)), required=True)
    end = fields.String(validate=(Predicate('isdigit'), Length(max=16)))

    def validate_range(self, start, end):
        if start > end:
            raise ValidationError('Start of range must be lower than or equal to the end')

    @validates_schema
    def validate_schema(self, data, **kwargs):
        if data.get('start') and data.get('end'):
            start = data.get('start')
            end = data.get('end')
            if len(start) != len(end):
                raise ValidationError('Start and end must be of the same length')
            self.validate_range(int(start), int(end))


class IncallRangeSchema(RangeSchema):
    did_length = fields.Integer(validate=Range(min=0))


class ContextSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(
        validate=(
            Regexp(CONTEXT_REGEX),
            Length(min=1, max=39),
            NoneOf([
                'authentication',
                'general',
                'global',
                'globals',
                'parkedcalls',
                'xivo-features',
                'zonemessages',
            ]),
        ),
        required=True,
    )
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
