# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length, Predicate, Range

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink


class ParkingLotSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(allow_none=True, validate=Length(max=128))
    slots_start = fields.String(
        validate=(Length(max=40), Predicate('isdigit')), required=True
    )
    slots_end = fields.String(
        validate=(Length(max=40), Predicate('isdigit')), required=True
    )
    timeout = fields.Integer(validate=Range(min=0), allow_none=True, missing=45)
    music_on_hold = fields.String(
        validate=Length(max=128), allow_none=True, missing='default'
    )
    links = ListLink(Link('parkinglots'))

    extensions = fields.Nested(
        'ExtensionSchema',
        only=['id', 'exten', 'context', 'links'],
        many=True,
        dump_only=True,
    )

    @validates_schema
    def validate_slots_range(self, data):
        # validates_schema is executed before fields validator, so the required
        # fields is not yet checked
        if not data.get('slots_start') or not data.get('slots_end'):
            return

        if int(data['slots_start']) > int(data['slots_end']):
            raise ValidationError('It is not a valid range')
