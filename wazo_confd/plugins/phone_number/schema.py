# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import ValidationError, fields, validates_schema
from marshmallow.validate import Length, Regexp

from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink
from .utils import PhoneNumberRangeSpec, PhoneNumberMainSpec

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
    links = fields.Method('build_links', dump_only=True)
    total = fields.Integer()

    def build_links(self, obj, **kwargs):
        link_factory = Link('phone_numbers', field='uuid')
        return [link_factory._serialize(None, None, entry) for entry in obj['links']]


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
        # NOTE(clanglois): both start_number and end_number are inclusive,
        # so range(start_number, start_number) -> [start_number]
        range_size = (
            int(data['end_number'].replace('+', ''))
            - int(data['start_number'].replace('+', ''))
            + 1
        )
        if not (1 <= range_size <= MAX_PHONE_NUMBER_RANGE_SIZE):
            raise ValidationError(
                f"range size must be between 1 and {MAX_PHONE_NUMBER_RANGE_SIZE}"
            )


class PhoneNumberMainSpecSchema(BaseSchema):
    phone_number_uuid = fields.UUID(required=True)

    def load(self, data, **kwargs) -> PhoneNumberMainSpec:
        data = super().load(data, **kwargs)
        return PhoneNumberMainSpec(
            phone_number_uuid=str(data['phone_number_uuid']),
        )


phone_number_schema = PhoneNumberSchema()
phone_number_range_spec_schema = PhoneNumberRangeSpecSchema()
phone_number_list_schema = PhoneNumberListSchema()
phone_number_main_spec_schema = PhoneNumberMainSpecSchema()
