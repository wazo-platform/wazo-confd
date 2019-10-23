# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re
import string
import logging

from marshmallow import fields, post_load
from marshmallow.validate import Length, Regexp, OneOf

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink

logger = logging.getLogger(__name__)

USERNAME_REGEX = r"^[a-zA-Z0-9_-]{1,40}$"
SECRET_REGEX = r"^[{}]{{1,80}}$".format(re.escape(string.printable))


class SipSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    username = fields.String(validate=Regexp(USERNAME_REGEX))
    name = fields.String(validate=Regexp(USERNAME_REGEX))
    secret = fields.String(validate=Regexp(SECRET_REGEX))
    type = fields.String(validate=OneOf(['friend', 'peer', 'user']))
    host = fields.String(validate=Length(max=255))
    options = fields.List(fields.List(fields.String(), validate=Length(equal=2)))
    links = ListLink(Link('endpoint_sip'))

    trunk = fields.Nested('TrunkSchema', only=['id', 'links'], dump_only=True)
    line = fields.Nested('LineSchema', only=['id', 'links'], dump_only=True)

    # The set_name_to_username_if_missing method is a compatibility method that
    # was added in 19.15 to avoid breaking the API. In the old version, the name
    # could not be specified in the API the username was always copied.
    @post_load
    def set_name_to_username_if_missing(self, data, **kwargs):
        name = data.get('name')
        if not name and 'username' in data:
            logger.warning(
                'DEPRECATION: creating a SIP endpoint with a "username" and no "name" is'
                ' deprecated. Populate the name field if it is required'
            )
            data['name'] = data['username']
        return data


class SipSchemaNullable(SipSchema):
    def on_bind_field(self, field_name, field_obj):
        super(SipSchemaNullable, self).on_bind_field(field_name, field_obj)
        nullable_fields = ['username', 'host', 'secret']
        if field_name in nullable_fields:
            field_obj.allow_none = True
