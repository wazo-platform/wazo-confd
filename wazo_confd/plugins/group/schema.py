# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from marshmallow import fields, post_dump, post_load, pre_load
from marshmallow.validate import Length, OneOf, Range, Regexp

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, Nested, StrictBoolean

# The label is going to end in queues.conf and used in agi.verbose calls.
# Try not to be too permissive with it
LABEL_REGEX = r'^[-_.a-zA-Z0-9 ]+$'

logger = logging.getLogger(__name__)


class GroupSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    uuid = fields.String(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(dump_only=True)
    label = fields.String(
        validate=[Length(max=128), Regexp(LABEL_REGEX)], required=True
    )
    preprocess_subroutine = fields.String(validate=Length(max=79), allow_none=True)
    ring_strategy = fields.String(
        validate=OneOf(
            [
                'all',
                'random',
                'least_recent',
                'linear',  # Issue when editing to this value: ASTERISK-17049
                'fewest_calls',
                'memorized_round_robin',
                'weight_random',
            ]
        )
    )
    caller_id_mode = fields.String(
        validate=OneOf(['prepend', 'overwrite', 'append']), allow_none=True
    )
    caller_id_name = fields.String(validate=Length(max=80), allow_none=True)
    dtmf_record_toggle = StrictBoolean()
    timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    user_timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    retry_delay = fields.Integer(validate=Range(min=0), allow_none=True)
    music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    ring_in_use = StrictBoolean()
    mark_answered_elsewhere = StrictBoolean(attribute='mark_answered_elsewhere_bool')
    enabled = StrictBoolean()
    max_calls = fields.Integer(validate=Range(min=0), allow_none=True)
    links = ListLink(Link('groups', field='uuid'))

    extensions = Nested(
        'ExtensionSchema',
        only=['id', 'exten', 'context', 'links'],
        many=True,
        dump_only=True,
    )
    fallbacks = Nested('GroupFallbackSchema', dump_only=True)
    incalls = Nested(
        'IncallSchema', only=['id', 'extensions', 'links'], many=True, dump_only=True
    )
    user_queue_members = Nested('GroupUsersMemberSchema', many=True, dump_only=True)
    extension_queue_members = Nested(
        'GroupExtensionsMemberSchema', many=True, dump_only=True
    )
    schedules = Nested(
        'ScheduleSchema', only=['id', 'name', 'links'], many=True, dump_only=True
    )
    call_permissions = Nested(
        'CallPermissionSchema', only=['id', 'name', 'links'], many=True, dump_only=True
    )

    # DEPRECATED 21.04
    @pre_load
    def copy_name_to_label(self, data, **kwargs):
        if 'label' in data:
            return data
        if 'name' in data:
            logger.warning(
                'the "name" field of groups is deprecated. use "label" instead'
            )
            data['label'] = data['name']
        return data

    @post_dump
    def convert_ring_strategy_to_user(self, data, **kwargs):
        ring_strategy = data.get('ring_strategy', None)
        if ring_strategy == 'ringall':
            data['ring_strategy'] = 'all'
        elif ring_strategy == 'leastrecent':
            data['ring_strategy'] = 'least_recent'
        elif ring_strategy == 'fewestcalls':
            data['ring_strategy'] = 'fewest_calls'
        elif ring_strategy == 'rrmemory':
            data['ring_strategy'] = 'memorized_round_robin'
        elif ring_strategy == 'wrandom':
            data['ring_strategy'] = 'weight_random'
        return data

    @post_dump
    def wrap_users_member(self, data, **kwargs):
        users_member = data.pop('user_queue_members', [])
        extensions_member = data.pop('extension_queue_members', [])
        if not self.only or 'members' in self.only:
            data['members'] = {'users': users_member, 'extensions': extensions_member}
        return data

    @post_load
    def convert_ring_strategy_to_database(self, data, **kwargs):
        ring_strategy = data.get('ring_strategy', None)
        if ring_strategy == 'all':
            data['ring_strategy'] = 'ringall'
        elif ring_strategy == 'least_recent':
            data['ring_strategy'] = 'leastrecent'
        elif ring_strategy == 'fewest_calls':
            data['ring_strategy'] = 'fewestcalls'
        elif ring_strategy == 'memorized_round_robin':
            data['ring_strategy'] = 'rrmemory'
        elif ring_strategy == 'weight_random':
            data['ring_strategy'] = 'wrandom'
        return data


class GroupUsersMemberSchema(BaseSchema):
    priority = fields.Integer()
    user = Nested(
        'UserSchema', only=['uuid', 'firstname', 'lastname', 'links'], dump_only=True
    )

    @post_dump
    def merge_user_group_member(self, data, **kwargs):
        user = data.pop('user', None)
        if not user:
            return data

        data['uuid'] = user.get('uuid', None)
        data['firstname'] = user.get('firstname', None)
        data['lastname'] = user.get('lastname', None)
        data['links'] = user.get('links', [])
        return data


class GroupExtensionsMemberSchema(BaseSchema):
    priority = fields.Integer()
    exten = fields.String(dump_only=True)
    context = fields.String(dump_only=True)
