# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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

from marshmallow import fields, validates_schema
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length, Predicate, Range

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class ParkingLotSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(allow_none=True, validate=Length(max=128))
    slots_start = fields.String(validate=(Length(max=40), Predicate('isdigit')), required=True)
    slots_end = fields.String(validate=(Length(max=40), Predicate('isdigit')), required=True)
    timeout = fields.Integer(validate=Range(min=0), allow_none=True)  # add default to 45 secondes
    music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    links = ListLink(Link('parkinglots'))

    extensions = fields.Nested('ExtensionSchema',
                               only=['id', 'exten', 'context', 'links'],
                               many=True,
                               dump_only=True)

    @validates_schema
    def validate_slots_range(self, data):
        # validates_schema is executed before fields validator, so the required
        # fields is not yet checked
        if not data.get('slots_start') or not data.get('slots_end'):
            return

        if int(data['slots_start']) > int(data['slots_end']):
            raise ValidationError('It is not a valid range')
