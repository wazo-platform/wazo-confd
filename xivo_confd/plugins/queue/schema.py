# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields, post_load, post_dump
from marshmallow.validate import Length, OneOf, Range, Regexp

from xivo_dao.alchemy.dialaction import Dialaction
from xivo_confd.helpers.destination import DestinationField
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean

NAME_REGEX = r'^[-_.a-zA-Z0-9]+$'


class QueueSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=(Regexp(NAME_REGEX), Length(max=128)), required=True)
    label = fields.String(validate=Length(max=128), missing=None)
    data_quality = StrictBoolean(attribute='data_quality_bool')
    dtmf_hangup_callee_enabled = StrictBoolean()
    dtmf_hangup_caller_enabled = StrictBoolean()
    dtmf_transfer_callee_enabled = StrictBoolean()
    dtmf_transfer_caller_enabled = StrictBoolean()
    dtmf_record_callee_enabled = StrictBoolean()
    dtmf_record_caller_enabled = StrictBoolean()
    retry_on_timeout = StrictBoolean()
    ring_on_hold = StrictBoolean()
    timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    announce_hold_time_on_entry = StrictBoolean()
    ignore_forward = StrictBoolean(attribute='ignore_forward_bool')
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    wait_time_threshold = fields.Integer(validate=Range(min=0), allow_none=True)
    wait_time_destination = DestinationField(allow_none=True)
    wait_ratio_threshold = fields.Float(validate=Range(min=0), allow_none=True)
    wait_ratio_destination = DestinationField(allow_none=True)
    caller_id_mode = fields.String(validate=OneOf(['prepend', 'overwrite', 'append']), allow_none=True)
    caller_id_name = fields.String(validate=Length(max=80), allow_none=True)
    enabled = StrictBoolean()
    options = fields.List(fields.List(fields.String(), validate=Length(equal=2)))
    links = ListLink(Link('queues'))

    extensions = fields.Nested(
        'ExtensionSchema',
        only=['id', 'exten', 'context', 'links'],
        many=True,
        dump_only=True,
    )
    schedules = fields.Nested(
        'ScheduleSchema',
        only=['id', 'name', 'links'],
        many=True,
        dump_only=True,
    )
    agent_queue_members = fields.Nested(
        'QueueAgentQueueMembersSchema',
        many=True,
        dump_only=True,
    )
    user_queue_members = fields.Nested(
        'QueueUserQueueMembersSchema',
        many=True,
        dump_only=True,
    )

    @post_load
    def create_objects(self, data):
        for key in ('wait_time_destination', 'wait_ratio_destination'):
            if data.get(key):
                data[key] = Dialaction(**data[key])

    @post_dump
    def wrap_members(self, data):
        if not self.only or 'members' in self.only:
            data['members'] = {
                'agents': data.pop('agent_queue_members', []),
                'users': data.pop('user_queue_members', []),
            }
        return data


class QueueAgentQueueMembersSchema(BaseSchema):
    priority = fields.Integer()
    penalty = fields.Integer()
    agent = fields.Nested(
        'AgentSchema',
        only=['id', 'number', 'firstname', 'lastname', 'links'],
    )

    @post_dump(pass_many=True)
    def merge_agent_queue_member(self, data, many):
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


class QueueUserQueueMembersSchema(BaseSchema):
    priority = fields.Integer()
    user = fields.Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
    )

    @post_dump(pass_many=True)
    def merge_user_queue_member(self, data, many):
        if not many:
            return self.merge_user(data)

        return [self._merge_user(row) for row in data if row.get('user')]

    def _merge_user(self, row):
        user = row.pop('user')
        row['uuid'] = user.get('uuid', None)
        row['firstname'] = user.get('firstname', None)
        row['lastname'] = user.get('lastname', None)
        row['links'] = user.get('links', [])
        return row


class QueueSchemaPUT(QueueSchema):
    name = fields.String(dump_only=True)
