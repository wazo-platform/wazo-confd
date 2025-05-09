# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import logging

import phonenumbers
from marshmallow import fields, validates
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, PhoneNumber
from wazo_confd.helpers.restful import ListSchema

logger = logging.getLogger(__name__)


class UserBlocklistNumberSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    number = PhoneNumber(required=True)
    label = fields.String(validate=Length(min=1, max=1024), allow_none=True)
    links = ListLink(Link('user_me_blocklist_numbers', field='uuid'))

    @validates('number')
    def validate_number(self, value: str):
        try:
            return phonenumbers.parse(value)
        except phonenumbers.NumberParseException as ex:
            logger.error('Invalid E.164 phone number: %s', str(ex))
            raise ValidationError(
                'Invalid E.164 phone number', field_name='number'
            ) from ex


class BlocklistNumberSchema(UserBlocklistNumberSchema):
    links = ListLink(Link('user_blocklist_numbers', field='uuid'))
    user_uuid = fields.String(dump_only=True)
    user_firstname = fields.String(dump_only=True, attribute='blocklist.user.firstname')
    user_lastname = fields.String(dump_only=True, attribute='blocklist.user.lastname')
    tenant_uuid = fields.String(dump_only=True, attribute='blocklist.tenant_uuid')


class BlocklistNumberListSchema(ListSchema):
    user_uuid = fields.String()
    number = PhoneNumber()
    label = fields.String(validate=Length(min=1, max=1024), allow_none=True)


class UserBlocklistLookupSchema(BaseSchema):
    number_exact = PhoneNumber()


user_blocklist_number_schema = UserBlocklistNumberSchema()
blocklist_number_schema = BlocklistNumberSchema()
user_blocklist_lookup_schema = UserBlocklistLookupSchema()
blocklist_number_list_schema = BlocklistNumberListSchema()
