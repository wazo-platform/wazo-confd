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


from marshmallow import fields
from marshmallow.validate import Length, Range

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class SwitchboardSchema(BaseSchema):
    id = fields.UUID(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    queue_music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    waiting_room_music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    links = ListLink(Link('switchboards'))
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
