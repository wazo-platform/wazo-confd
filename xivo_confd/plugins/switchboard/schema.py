# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+


from marshmallow import fields
from marshmallow import post_dump
from marshmallow.validate import Length, Range

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class SwitchboardSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    queue_music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    waiting_room_music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    links = ListLink(Link('switchboards', field='uuid'))
    extensions = fields.Nested('ExtensionSchema',
                               only=['id', 'exten', 'context', 'links'],
                               many=True,
                               dump_only=True)
    incalls = fields.Nested('IncallSchema',
                            only=['id',
                                  'extensions',
                                  'links'],
                            many=True,
                            dump_only=True)

    user_members = fields.Nested('UserSchema',
                                 only=['uuid', 'firstname', 'lastname', 'links'],
                                 many=True,
                                 dump_only=True)

    @post_dump
    def wrap_users(self, data):
        user_members = data.pop('user_members', [])
        if not self.only or 'members' in self.only:
            data['members'] = {'users': user_members}
        return data
