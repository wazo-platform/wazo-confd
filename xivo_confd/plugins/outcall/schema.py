# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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
from marshmallow.validate import Length, Range, Regexp

from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink


PATTERN_REGEX = r'^_?\+?[0-9NXZ*#\-\[\]]+[.!]?$'
EXTERNAL_PREFIX_REGEX = r'^\+|\+?[0-9#*]+$'
PREFIX_REGEX = r'^\+|\+?[0-9#*]+$'


class OutcallPatternSchema(BaseSchema):
    pattern = fields.String(validate=(Length(max=40), Regexp(PATTERN_REGEX)), required=True)
    caller_id = fields.String(validate=Length(max=80), allow_none=True)
    external_prefix = fields.String(validate=(Length(max=64), Regexp(EXTERNAL_PREFIX_REGEX)), allow_none=True)
    prefix = fields.String(validate=(Length(max=32), Regexp(PREFIX_REGEX)), allow_none=True)
    strip_digits = fields.Integer(validate=Range(min=0))


class OutcallSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    context = fields.String(required=True)
    internal_caller_id = StrictBoolean()
    preprocess_subroutine = fields.String(validate=Length(max=39))
    ring_time = fields.Integer(validate=Range(min=0), allow_none=True)
    description = fields.String(allow_none=True)
    patterns = fields.Nested(OutcallPatternSchema, many=True)
    links = ListLink(Link('outcalls'))
