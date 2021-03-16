# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load, pre_dump
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema


class _RewriteRule(BaseSchema):
    match = fields.String()
    replacement = fields.String()


class EmailConfigSchema(BaseSchema):
    domain_name = fields.String(validate=Length(max=255), missing='')
    from_ = fields.String(data_key='from', validate=Length(max=255), missing='')
    address_rewriting_rules = fields.List(fields.Nested(_RewriteRule), missing=[])
    smtp_host = fields.String(validate=Length(max=255), missing='')
    fallback_smtp_host = fields.String(validate=Length(max=255), missing='')

    def _rewriting_rules_from_db(self, canonical):
        rules = []
        for line in canonical.splitlines():
            match, replacement = line.split(maxsplit=1)
            rules.append({'match': match, 'replacement': replacement})
        return rules

    def _rewriting_rules_to_db(self, rules):
        lines = [f"{rule['match']} {rule['replacement']}" for rule in rules]
        return '\n'.join(lines)

    @pre_dump
    def from_db_model(self, data, **kwargs):
        result = {
            'domain_name': data.mydomain,
            'from_': data.origin,
            'address_rewriting_rules': self._rewriting_rules_from_db(data.canonical),
            'smtp_host': data.relayhost,
            'fallback_smtp_host': data.fallback_relayhost,
        }
        return result

    @post_load
    def to_db_model(self, data, **kwargs):
        result = {
            'mydomain': data['domain_name'],
            'origin': data['from_'],
            'canonical': self._rewriting_rules_to_db(data['address_rewriting_rules']),
            'relayhost': data['smtp_host'],
            'fallback_relayhost': data['fallback_smtp_host'],
        }
        return result
