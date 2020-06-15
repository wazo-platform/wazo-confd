# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re
import string
import logging
import random

from marshmallow import fields, EXCLUDE, post_load
from marshmallow.validate import Length, Regexp

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink

logger = logging.getLogger(__name__)

USERNAME_REGEX = r"^[a-zA-Z0-9_+-]{1,40}$"
SECRET_REGEX = r"^[{}]{{1,80}}$".format(re.escape(string.printable))
ASTERISK_SECTION_NAME_REGEX = r"^[a-zA-Z0-9-_]*$"
ASTERISK_OPTION_VALUE_NAME_REGEX = r"^[a-zA-Z0-9-_\/\.:]*$"

options_field = fields.List(
    fields.List(
        fields.String(validate=Length(min=1, max=4092)), validate=Length(min=1, max=2),
    ),
    missing=[],
)


class EndpointSIPRelationSchema(BaseSchema):
    uuid = fields.UUID(required=True)


class TransportRelationSchema(BaseSchema):
    uuid = fields.UUID(required=True)


class ContextRelationSchema(BaseSchema):
    id = fields.Integer(required=True)


class EndpointSIPSchema(BaseSchema):

    uuid = fields.UUID(dump_only=True)
    tenant_uuid = fields.UUID(dump_only=True)
    name = fields.String(
        validate=(Regexp(ASTERISK_SECTION_NAME_REGEX), Length(min=1, max=128)),
        missing=None,
    )
    label = fields.String(validate=Length(max=128))
    template = fields.Boolean(missing=False)

    aor_section_options = options_field
    auth_section_options = options_field
    endpoint_section_options = options_field
    identify_section_options = options_field
    registration_section_options = options_field
    registration_outbound_auth_section_options = options_field
    outbound_auth_section_options = options_field

    parents = fields.List(
        fields.Nested('EndpointSIPRelationSchema', unknown=EXCLUDE), missing=[]
    )
    transport = fields.Nested('TransportRelationSchema', unknown=EXCLUDE)
    context = fields.Nested('ContextRelationSchema', unknown=EXCLUDE)
    asterisk_id = fields.String(validate=Length(max=1024))

    links = ListLink(Link('endpoint_sip', field='uuid'))

    trunk = fields.Nested('TrunkSchema', only=['id', 'links'], dump_only=True)
    line = fields.Nested('LineSchema', only=['id', 'links'], dump_only=True)


class EndpointSIPSchemaNullable(EndpointSIPSchema):

    username = fields.String(validate=Regexp(USERNAME_REGEX), missing=None)
    secret = fields.String(validate=Regexp(SECRET_REGEX), missing=None)

    @post_load
    def assign_username_and_password(self, data):
        username = data.pop('username', None) or random_string(8)
        password = data.pop('secret', None) or random_string(8)
        data['auth_section_options'] = [
            ['username', username],
            ['password', password],
        ]
        return data


def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))
