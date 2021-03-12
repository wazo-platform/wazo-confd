# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load, pre_dump
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema


class _RewriteRule(BaseSchema):
    match = fields.String()
    replacement = fields.String()


class EmailConfigSchema(BaseSchema):
    domain_name = fields.String(validate=Length(max=255))
    from_ = fields.String(data_key='from', validate=Length(max=255))
    address_rewriting_rules = fields.List(fields.Nested(_RewriteRule))
    smtp_host = fields.String(validate=Length(max=255))
    fallback_smtp_host = fields.String(validate=Length(max=255))
