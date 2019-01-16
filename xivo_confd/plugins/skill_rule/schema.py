# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load, pre_dump
from marshmallow.validate import Length, Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink

NAME_REGEX = r'^[-_.a-zA-Z0-9]+$'


class SkillRuleSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=(Regexp(NAME_REGEX), Length(max=64)), required=True)
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
