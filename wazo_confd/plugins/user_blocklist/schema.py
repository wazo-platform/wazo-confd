# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import phonenumbers
from marshmallow import fields, validates
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, number_field


class UserBlocklistNumberSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    number = number_field(required=True)
    label = fields.String(validate=Length(min=1, max=1024), allow_none=True)
    links = ListLink(Link('user_me_blocklist_numbers', field='uuid'))

    @validates('number')
    def validate_number(self, value: str):
        try:
            return phonenumbers.parse(value)
        except phonenumbers.NumberParseException:
            raise ValidationError('Invalid E.164 phone number', field_name='number')


user_blocklist_number_schema = UserBlocklistNumberSchema()
