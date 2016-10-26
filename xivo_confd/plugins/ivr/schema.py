# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from marshmallow import fields, post_load
from marshmallow.validate import Length, Range, Regexp
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.ivr_choice import IVRChoice

from xivo_confd.helpers.destination import DestinationField
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.validator import EXTEN_REGEX


class IvrChoiceSchema(BaseSchema):
    exten = fields.String(validate=Regexp(EXTEN_REGEX), required=True)
    destination = DestinationField(required=True)


class IvrSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    description = fields.String(allow_none=True)
    greeting_sound = fields.String(validate=Length(max=255), allow_none=True)
    menu_sound = fields.String(validate=Length(max=255), required=True)
    invalid_sound = fields.String(validate=Length(max=255), allow_none=True)
    abort_sound = fields.String(validate=Length(max=255), allow_none=True)
    timeout = fields.Integer(validate=Range(min=0))
    max_tries = fields.Integer(validate=Range(min=1))
    invalid_destination = DestinationField(allow_none=True)
    timeout_destination = DestinationField(allow_none=True)
    abort_destination = DestinationField(allow_none=True)
    choices = fields.Nested(IvrChoiceSchema, many=True)
    links = ListLink(Link('ivr'))

    @post_load
    def create_objects(self, data):
        for key in ['invalid_destination', 'timeout_destination', 'abort_destination']:
            if data.get(key):
                data[key] = Dialaction(**data[key])
        if 'choices' in data:
            data['choices'] = [
                IVRChoice(exten=choice['exten'], destination=Dialaction(**choice['destination']))
                for choice in data['choices']
            ]
