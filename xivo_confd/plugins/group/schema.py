# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


from marshmallow import fields, post_load, post_dump
from marshmallow.validate import Length, Range, OneOf

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean


class GroupMembersSchema(BaseSchema):
    users = fields.Nested('UserSchema',
                          only=['uuid', 'firstname', 'lastname', 'links'],
                          many=True,
                          dummp_only=True)


class GroupSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    ring_strategy = fields.String(validate=OneOf([
        'all',
        'random',
        'least_recent',
        'linear',  # Issue when editing to this value: ASTERISK-17049
        'fewest_calls',
        'memorized_round_robin',
        'weight_random'
    ]))
    caller_id_mode = fields.String(validate=OneOf(['prepend', 'overwrite', 'append']), allow_none=True)
    caller_id_name = fields.String(validate=Length(max=80), allow_none=True)
    timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    user_timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    retry_delay = fields.Integer(validate=Range(min=0), allow_none=True)
    music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    ring_in_use = StrictBoolean()
    enabled = StrictBoolean()
    links = ListLink(Link('groups'))

    extensions = fields.Nested('ExtensionSchema',
                               only=['id', 'exten', 'context', 'links'],
                               many=True,
                               dump_only=True)
    members = fields.Nested('GroupMembersSchema',
                            dump_only=True)

    @post_dump
    def convert_ring_strategy_to_user(self, data):
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

    @post_load
    def convert_ring_strategy_to_database(self, data):
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
