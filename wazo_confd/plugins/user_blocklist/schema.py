# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, number_field


class UserBlocklistNumberSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    # user_uuid = fields.UUID(dump_only=True)
    number = number_field(required=True)
    label = fields.String(validate=Length(min=1, max=1024), allow_none=True)
    links = ListLink(Link('user_me_blocklist_numbers', field='uuid'))


user_blocklist_number_schema = UserBlocklistNumberSchema()
