# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from marshmallow import fields, post_load, pre_load, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length, OneOf, Predicate, Range

from xivo_dao.alchemy.contextnumbers import ContextNumbers

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean, Nested

CONTEXT_REGEX = r"^[a-zA-Z0-9-_]*$"
logger = logging.getLogger(__name__)


class RangeSchema(BaseSchema):
    start = fields.String(
        validate=(Predicate('isdigit'), Length(max=16)), required=True
    )
    end = fields.String(validate=(Predicate('isdigit'), Length(max=16)))

    def validate_range(self, start, end):
        if start > end:
            raise ValidationError(
                'Start of range must be lower than or equal to the end'
            )

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
    name = fields.String(dump_only=True)
    label = fields.String(validate=Length(min=1, max=128), required=True)
    type = fields.String(
        validate=OneOf(['internal', 'incall', 'outcall', 'services', 'others'])
    )
    user_ranges = Nested(RangeSchema, many=True)
    group_ranges = Nested(RangeSchema, many=True)
    queue_ranges = Nested(RangeSchema, many=True)
    conference_room_ranges = Nested(RangeSchema, many=True)
    incall_ranges = Nested(IncallRangeSchema, many=True)
    description = fields.String(allow_none=True)
    tenant_uuid = fields.String(dump_only=True)
    enabled = StrictBoolean()
    links = ListLink(Link('contexts'))

    contexts = Nested(
        'ContextSchema',
        only=['id', 'name', 'label', 'links'],
        many=True,
        dump_only=True,
    )

    @post_load
    def create_objects(self, data, **kwargs):
        for key in [
            'user_ranges',
            'group_ranges',
            'queue_ranges',
            'conference_room_ranges',
            'incall_ranges',
        ]:
            if data.get(key):
                data[key] = [ContextNumbers(**d) for d in data[key]]
        return data

    # DEPRECATED 23.10
    @pre_load
    def copy_name_to_label(self, data, **kwargs):
        if 'label' in data:
            return data
        if 'name' in data:
            logger.warning(
                'The "name" field of context is deprecated. Use "label" instead'
            )
            data['label'] = data['name']
        return data


class ContextSchemaPUT(ContextSchema):
    name = fields.String(dump_only=True)
