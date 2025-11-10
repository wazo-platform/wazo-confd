# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import ValidationError, fields, validates_schema
from marshmallow.validate import Length, OneOf, Range, Regexp

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, Nested, StrictBoolean
from wazo_confd.helpers.validator import LANGUAGE_REGEX

NUMBER_REGEX = r"^[0-9]{1,40}$"
PASSWORD_REGEX = r"^[0-9]{1,80}$"


class VoicemailSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(validate=Length(max=80), required=True)
    number = fields.String(validate=Regexp(NUMBER_REGEX), required=True)
    context = fields.String(required=True)
    password = fields.String(validate=Regexp(PASSWORD_REGEX), allow_none=True)
    email = fields.String(validate=Length(max=80), allow_none=True)
    language = fields.String(validate=Regexp(LANGUAGE_REGEX), allow_none=True)
    timezone = fields.String(allow_none=True)
    pager = fields.String(validate=Length(max=80), allow_none=True)
    max_messages = fields.Integer(validate=Range(min=0), allow_none=True)
    attach_audio = StrictBoolean(allow_none=True)
    delete_messages = StrictBoolean()
    ask_password = StrictBoolean()
    enabled = StrictBoolean()
    options = fields.List(fields.List(fields.String(), validate=Length(equal=2)))
    links = ListLink(Link('voicemails'))
    accesstype = fields.String(
        validate=OneOf(['personal', 'global']),
        load_default='personal',
        dump_default='personal',
    )

    users = Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )

    @validates_schema
    def prevent_delete_messages_without_email_and_attach_audio(self, data, **kwargs):
        if data.get('delete_messages', False) and not data.get('email', None):
            raise ValidationError('email must be provided if delete_messages is set')
        if data.get('delete_messages', False) and not data.get('attach_audio', None):
            raise ValidationError('attach_audio must be set if delete_messages is set')


class UserVoicemailSchema(VoicemailSchema):
    id = fields.Integer()
    name = fields.String(validate=Length(max=80))
    number = fields.String(validate=Regexp(NUMBER_REGEX))
    context = fields.String()

    @validates_schema
    def check_required_fields(self, data, **kwargs):
        voicemail_id = data.get('id', None)
        name = data.get('name', None)
        number = data.get('number', None)
        context = data.get('context', None)
        if not voicemail_id:
            if not name and not number and not context:
                raise ValidationError(
                    'name, number and context must be provided if no id provided'
                )
