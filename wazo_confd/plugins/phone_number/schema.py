# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import ValidationError, fields, validates_schema
from marshmallow.validate import Length, Regexp

from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink
from .utils import PhoneNumberRangeSpec

MAX_PHONE_NUMBER_RANGE_SIZE = 10_000


def number_field(**kwargs):
    return fields.String(
        validate=[
            Length(min=1, max=128),
            Regexp(r'^\+?[0-9]+$', error='not a valid digit-only phone number'),
        ],
        **kwargs,
    )


class PhoneNumberSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    number = number_field(required=True)
    caller_id_name = fields.String(validate=Length(min=1, max=256), allow_none=True)
    main = StrictBoolean(default=False)
    shared = StrictBoolean(default=False)
    links = ListLink(Link('phone_numbers', field='uuid'))


class PhoneNumberListSchema(BaseSchema):
    """
    Response to phone number range creation API
    """

    created = fields.Nested(PhoneNumberSchema, many=True, only=['uuid'])
    links = ListLink(Link('phone_numbers', field='uuid'))
    total = fields.Integer()


class PhoneNumberRangeSpecSchema(BaseSchema):
    start_number = number_field(required=True)
    end_number = number_field(required=True)

    def load(self, data, **kwargs) -> PhoneNumberRangeSpec:
        data = super().load(data, **kwargs)
        return PhoneNumberRangeSpec(
            start_number=data['start_number'],
            end_number=data['end_number'],
        )

    @validates_schema()
    def validate_range(self, data, **kwargs):
        if not (data['start_number'] <= data['end_number']):
            raise ValidationError("start phone number must precede end phone number")
        range_size = int(data['end_number'].replace('+', '')) - int(
            data['start_number'].replace('+', '')
        )
        if not (1 <= range_size <= MAX_PHONE_NUMBER_RANGE_SIZE):
            raise ValidationError(
                f"range size must be between 1 and {MAX_PHONE_NUMBER_RANGE_SIZE}"
            )


phone_number_schema = PhoneNumberSchema()
phone_number_range_spec_schema = PhoneNumberRangeSpecSchema()
phone_number_list_schema = PhoneNumberListSchema()
