# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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
