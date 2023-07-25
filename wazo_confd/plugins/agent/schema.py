# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_dump
from marshmallow.validate import Length, Regexp

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, Nested

NUMBER_REGEX = r"^[0-9\*#]{1,40}$"


class AgentSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    number = fields.String(validate=Regexp(NUMBER_REGEX), required=True)
    firstname = fields.String(validate=Length(max=128), allow_none=True)
    lastname = fields.String(validate=Length(max=128), allow_none=True)
    password = fields.String(
        validate=Length(max=128), allow_none=True, attribute='passwd'
    )
    language = fields.String(validate=Length(max=20), allow_none=True)
    preprocess_subroutine = fields.String(validate=Length(max=79),  allow_none=True)
    description = fields.String(allow_none=True)
    links = ListLink(Link('agents'))

    queues = Nested(
        'AgentQueuesMemberSchema',
        attribute='queue_queue_members',
        many=True,
        dump_only=True,
    )
    skills = Nested(
        'AgentSkillsSchema', attribute='agent_queue_skills', many=True, dump_only=True
    )
    users = Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )


class AgentQueuesMemberSchema(BaseSchema):
    penalty = fields.Integer()
    queue = Nested('QueueSchema', only=['id', 'name', 'label', 'links'], dump_only=True)

    @post_dump
    def merge_queue_queue_member(self, data, **kwargs):
        queue = data.pop('queue', None)
        if not queue:
            return data

        data['id'] = queue.get('id', None)
        data['name'] = queue.get('name', None)
        data['label'] = queue.get('label', None)
        data['links'] = queue.get('links', [])
        return data


class AgentSkillsSchema(BaseSchema):
    skill_weight = fields.Integer(attribute='weight')
    skill = Nested('SkillSchema', only=['id', 'name', 'links'], dump_only=True)

    @post_dump
    def merge_agent_queue_skills(self, data, **kwargs):
        skill = data.pop('skill', None)
        if not skill:
            return data

        data['id'] = skill.get('id', None)
        data['name'] = skill.get('name', None)
        data['links'] = skill.get('links', [])
        return data


class AgentSchemaPUT(AgentSchema):
    number = fields.String(dump_only=True)
