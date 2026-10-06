# Copyright 2024-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import ValidationError, fields, post_dump, validates_schema
from marshmallow.validate import OneOf

from wazo_confd.helpers.mallow import BaseSchema, PhoneNumber

from .service import CallerID

# types that carry a number, as opposed to the routing tokens
NUMBER_TYPES = ('main', 'associated', 'shared')
# `custom` is reported by the API, never accepted
SETTABLE_TYPES = NUMBER_TYPES + ('default', 'anonymous')


class UserCallerIDSchema(BaseSchema):
    number = fields.String(dump_only=True)
    type = fields.String(dump_only=True)
    caller_id_name = fields.String(dump_only=True)

    @post_dump
    def omit_fields_for_anonymous(self, data, **kwargs):
        if data.get('type') == 'anonymous':
            data.pop('number', None)
            data.pop('caller_id_name', None)
        return data


class UserCallerIDDefaultSchema(BaseSchema):
    type = fields.String(required=True, validate=OneOf(SETTABLE_TYPES))
    number = PhoneNumber(load_default='')
    caller_id_name = fields.String(dump_only=True)

    @validates_schema
    def validate_number_presence(self, data, **kwargs):
        if data.get('type') in NUMBER_TYPES and not data.get('number'):
            raise ValidationError(
                f'number is required when type is one of {list(NUMBER_TYPES)}',
                'number',
            )

    def load(self, data, **kwargs) -> CallerID:
        data = super().load(data, **kwargs)
        return CallerID(type=data['type'], number=data['number'])

    @post_dump
    def omit_number_for_tokens(self, data, **kwargs):
        if data.get('type') in ('default', 'anonymous'):
            data.pop('number', None)
            data.pop('caller_id_name', None)
        return data
