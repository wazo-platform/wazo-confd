# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink


class PhoneNumberSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    number = fields.String(validate=Length(min=1, max=128), required=True)
    caller_id_name = fields.String(validate=Length(min=1, max=256), allow_none=True)
    main = StrictBoolean(default=False)
    shared = StrictBoolean(default=False)
    links = ListLink(Link('phone_numbers', field='uuid'))


phone_number_schema = PhoneNumberSchema()
