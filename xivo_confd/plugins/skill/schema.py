# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_dump
from marshmallow.validate import Length, Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink

NAME_REGEX = r'^[-_.a-zA-Z0-9]+$'


class SkillSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(validate=(Regexp(NAME_REGEX), Length(max=64)), required=True)
    category = fields.String(validate=Length(max=64), allow_none=True)
    description = fields.String(allow_none=True)
    links = ListLink(Link('skills'))

    agents = fields.Nested(
        'SkillAgentsSchema',
        attribute='agent_queue_skills',
        many=True,
        dump_only=True,
    )


class SkillAgentsSchema(BaseSchema):
    skill_weight = fields.Integer(attribute='weight')
    agent = fields.Nested(
        'AgentSchema',
        only=['id', 'number', 'firstname', 'lastname', 'links'],
        dump_only=True,
    )

    @post_dump(pass_many=True)
    def merge_agent_queue_skills(self, data, many):
        if not many:
            return self.merge_agent(data)

        return [self._merge_agent(row) for row in data if row.get('agent')]

    def _merge_agent(self, row):
        agent = row.pop('agent')
        row['id'] = agent.get('id', None)
        row['number'] = agent.get('number', None)
        row['firstname'] = agent.get('firstname', None)
        row['lastname'] = agent.get('lastname', None)
        row['links'] = agent.get('links', [])
        return row
