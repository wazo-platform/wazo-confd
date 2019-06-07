# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load, pre_dump
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink


class SkillRuleSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(validate=(Length(max=64)), required=True)
    rules = fields.Nested('SkillRuleRuleSchema', many=True, allow_none=True)
    links = ListLink(Link('skillrules'))


class SkillRuleRuleSchema(BaseSchema):
    definition = fields.String(required=True)

    @post_load
    def remove_envelope(self, data):
        return data['definition']

    @pre_dump
    def add_envelope(self, data):
        return {'definition': data}
