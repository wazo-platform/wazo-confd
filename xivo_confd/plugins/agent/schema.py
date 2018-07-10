# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields, post_dump
from marshmallow.validate import Length, Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink

NUMBER_REGEX = r"^[0-9\*#]{1,40}$"


class AgentSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    number = fields.String(validate=Regexp(NUMBER_REGEX), required=True)
    firstname = fields.String(validate=Length(max=128), allow_none=True)
    lastname = fields.String(validate=Length(max=128), allow_none=True)
    password = fields.String(validate=Length(max=128), allow_none=True, attribute='passwd')
    language = fields.String(validate=Length(max=20), allow_none=True)
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    description = fields.String(allow_none=True)
    links = ListLink(Link('agents'))

    queues = fields.Nested(
        'AgentQueuesMemberSchema',
        attribute='queue_queue_members',
        many=True,
        dump_only=True,
    )


class AgentQueuesMemberSchema(BaseSchema):
    penalty = fields.Integer()
    queue = fields.Nested(
        'QueueSchema',
        only=['id', 'name', 'label', 'links'],
        dump_only=True,
    )

    @post_dump(pass_many=True)
    def merge_queue_queue_member(self, data, many):
        if not many:
            return self.merge_queue(data)

        return [self._merge_queue(row) for row in data if row.get('queue')]

    def _merge_queue(self, row):
        queue = row.pop('queue')
        row['id'] = queue.get('id', None)
        row['name'] = queue.get('name', None)
        row['label'] = queue.get('label', None)
        row['links'] = queue.get('links', [])
        return row


class AgentSchemaPUT(AgentSchema):
    number = fields.String(dump_only=True)