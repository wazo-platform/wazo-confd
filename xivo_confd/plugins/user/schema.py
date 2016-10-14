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

from xivo_confd.helpers.validator import LANGUAGE_REGEX
from marshmallow import fields
from marshmallow.validate import Length, Range, Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean


MOBILE_PHONE_NUMBER_REGEX = r"^\+?[0-9\*#]+$"
CALLER_ID_REGEX = r'^"(.*)"( <\+?\d+>)?$'
USERNAME_REGEX = r"^[a-zA-Z0-9-\._~\!\$&\'\(\)\*\+,;=%@]{2,254}$"
PASSWORD_REGEX = r"^[a-zA-Z0-9-\._~\!\$&\'\(\)\*\+,;=%]{4,64}$"
CALL_PERMISSION_PASSWORD_REGEX = r"^[0-9#\*]{1,16}$"


class UserSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    uuid = fields.String(dump_only=True)
    firstname = fields.String(validate=Length(max=128), required=True)
    lastname = fields.String(validate=Length(max=128), allow_none=True)
    email = fields.String(validate=Length(max=254), allow_none=True)
    timezone = fields.String(validate=Length(max=128), allow_none=True)
    language = fields.String(validate=Regexp(LANGUAGE_REGEX), allow_none=True)
    description = fields.String(allow_none=True)
    caller_id = fields.String(validate=(Regexp(CALLER_ID_REGEX), Length(max=160)))
    outgoing_caller_id = fields.String(validate=Length(max=80), allow_none=True)
    mobile_phone_number = fields.String(validate=(Regexp(MOBILE_PHONE_NUMBER_REGEX), Length(max=80)), allow_none=True)
    username = fields.String(validate=Regexp(USERNAME_REGEX), allow_none=True)
    password = fields.String(validate=Regexp(PASSWORD_REGEX), allow_none=True)
    music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    userfield = fields.String(validate=Length(max=128), allow_none=True)
    call_transfer_enabled = StrictBoolean()
    dtmf_hangup_enabled = StrictBoolean()
    call_record_enabled = StrictBoolean()
    online_call_record_enabled = StrictBoolean()
    supervision_enabled = StrictBoolean()
    ring_seconds = fields.Integer(validate=Range(min=0, max=60))
    simultaneous_calls = fields.Integer(validate=Range(min=1, max=20))
    call_permission_password = fields.String(validate=Regexp(CALL_PERMISSION_PASSWORD_REGEX), allow_none=True)
    enabled = StrictBoolean()
    links = ListLink(Link('users'))


class UserDirectorySchema(BaseSchema):
    id = fields.Integer()
    uuid = fields.String()
    line_id = fields.Integer(default=None)
    agent_id = fields.String(default=None)
    firstname = fields.String()
    lastname = fields.String()
    email = fields.String()
    exten = fields.String()
    mobile_phone_number = fields.String()
    voicemail_number = fields.String()
    userfield = fields.String()
    description = fields.String()
    context = fields.String()


class UserSummarySchema(BaseSchema):
    id = fields.Integer()
    uuid = fields.String()
    firstname = fields.String()
    lastname = fields.String()
    email = fields.String()
    extension = fields.String()
    context = fields.String()
    provisioning_code = fields.String()
    entity = fields.String()
    protocol = fields.String()
    enabled = StrictBoolean()


class UserSchemaNullable(UserSchema):

    def on_bind_field(self, field_name, field_obj):
        super(UserSchemaNullable, self).on_bind_field(field_name, field_obj)
        nullable_fields = ['call_record_enabled',
                           'call_transfer_enabled',
                           'caller_id',
                           'dtmf_hangup_enabled',
                           'enabled',
                           'online_call_record_enabled',
                           'ring_seconds',
                           'supervision_enabled']
        if field_name in nullable_fields:
            field_obj.allow_none = True
