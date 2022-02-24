# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load, pre_dump
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema, Nested


class _RewriteRule(BaseSchema):
    match = fields.String(required=True)
    replacement = fields.String(required=True)

    @pre_dump
    def from_canonical(self, data, **kwargs):
        match, replacement = data.split(maxsplit=1)
        return {'match': match, 'replacement': replacement}

    @post_load
    def to_canonical(self, data, **kwargs):
        return f"{data['match']} {data['replacement']}"


class EmailConfigSchema(BaseSchema):
    domain_name = fields.String(
        attribute='mydomain', validate=Length(max=255), missing=''
    )
    from_ = fields.String(
        attribute='origin', data_key='from', validate=Length(max=255), missing=''
    )
    address_rewriting_rules = fields.List(
        Nested(_RewriteRule, missing=None),
        attribute='canonical_lines',
        missing=[],
    )
    smtp_host = fields.String(
        attribute='relayhost', validate=Length(max=255), missing=''
    )
    fallback_smtp_host = fields.String(
        attribute='fallback_relayhost', validate=Length(max=255), missing=''
    )

    @pre_dump
    def split_canonical(self, data, **kwargs):
        data.canonical_lines = [line for line in data.canonical.split('\\n') if line]
        return data

    @post_load
    def join_canonical(self, data, **kwargs):
        data['canonical'] = '\\n'.join(data.get('canonical_lines', []))
        return data
