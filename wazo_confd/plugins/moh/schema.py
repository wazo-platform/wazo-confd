# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import secrets
import string

from marshmallow import fields, post_load
from marshmallow.validate import Length, OneOf

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, AsteriskSection

# the regex is more restrictive since the name is used both for the Asterisk
# section and the directory on the file system
moh_name_validator = AsteriskSection(
    max_length=20, regex=r'^[a-zA-Z0-9][-_.a-zA-Z0-9]*$'
)


class MohFileSchema(BaseSchema):
    name = fields.String()


class MohSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(validate=moh_name_validator, required=True)
    label = fields.String(validate=Length(max=128), allow_none=True)
    mode = fields.String(validate=OneOf(['custom', 'files', 'mp3']), required=True)
    application = fields.String(validate=Length(max=256), allow_none=True)
    sort = fields.String(
        validate=OneOf(['alphabetical', 'random', 'random_start']), allow_none=True
    )
    files = fields.Nested(MohFileSchema, many=True, dump_only=True)

    links = ListLink(Link('moh', field='uuid'))

    def _generate_random_characters(self, length=16):
        return ''.join(secrets.choice(string.ascii_letters) for _ in range(length))

    @post_load
    def suffix_name_with_random_characters(self, data):
        if 'name' in data:
            data['name'] = data['name'] + '-' + self._generate_random_characters()
        return data


class MohSchemaPUT(MohSchema):
    name = fields.String(dump_only=True)
