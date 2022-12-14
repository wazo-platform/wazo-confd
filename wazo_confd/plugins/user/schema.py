# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import (
    fields,
    post_dump,
    pre_dump,
    pre_load,
    post_load,
    validates_schema,
)
from marshmallow.exceptions import ValidationError
from marshmallow.validate import Length, Range, Regexp, OneOf

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean, Nested
from wazo_confd.helpers.validator import LANGUAGE_REGEX
from wazo_confd.plugins.agent.schema import AgentSchema, NUMBER_REGEX
from wazo_confd.plugins.line.schema import LineSchema

MOBILE_PHONE_NUMBER_REGEX = r"^\+?[0-9\*#]+$"
CALLER_ID_REGEX = r'^"(.*)"( <\+?\d+>)?$'
USERNAME_REGEX = r"^[a-zA-Z0-9-\._~\!\$&\'\(\)\*\+,;=%@]{2,254}$"
PASSWORD_REGEX = r"^[a-zA-Z0-9-\._~\!\$&\'\(\)\*\+,;=%]{4,64}$"
CALL_PERMISSION_PASSWORD_REGEX = r"^[0-9#\*]{1,16}$"


class WazoAuthUserSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    username = fields.String(
        validate=Length(min=1, max=256), missing=None, allow_none=True
    )
    password = fields.String(validate=Length(min=1), allow_none=True)
    firstname = fields.String(missing=None, allow_none=True)
    lastname = fields.String(missing=None, allow_none=True)
    purpose = fields.String(
        missing='user', validate=OneOf(['user', 'internal', 'external_api'])
    )
    enabled = fields.Boolean(missing=True)
    email_address = fields.Email(allow_none=True)


class UserSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    uuid = fields.String(dump_only=True)
    firstname = fields.String(validate=Length(max=128), required=True)
    lastname = fields.String(validate=Length(max=128), allow_none=True)
    email = fields.Email(validate=Length(max=254), allow_none=True)
    timezone = fields.String(validate=Length(max=128), allow_none=True)
    language = fields.String(validate=Regexp(LANGUAGE_REGEX), allow_none=True)
    description = fields.String(allow_none=True)
    caller_id = fields.String(validate=(Regexp(CALLER_ID_REGEX), Length(max=160)))
    outgoing_caller_id = fields.String(validate=Length(max=80), allow_none=True)
    mobile_phone_number = fields.String(
        validate=(Regexp(MOBILE_PHONE_NUMBER_REGEX), Length(max=80)), allow_none=True
    )
    username = fields.String(validate=Regexp(USERNAME_REGEX), allow_none=True)
    password = fields.String(validate=Regexp(PASSWORD_REGEX), allow_none=True)
    music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    userfield = fields.String(validate=Length(max=128), allow_none=True)
    call_transfer_enabled = StrictBoolean()
    dtmf_hangup_enabled = StrictBoolean()
    call_record_enabled = StrictBoolean()
    call_record_outgoing_external_enabled = StrictBoolean()
    call_record_outgoing_internal_enabled = StrictBoolean()
    call_record_incoming_internal_enabled = StrictBoolean()
    call_record_incoming_external_enabled = StrictBoolean()
    online_call_record_enabled = StrictBoolean()
    supervision_enabled = StrictBoolean()
    ring_seconds = fields.Integer(validate=Range(min=0, max=10800))
    simultaneous_calls = fields.Integer(validate=Range(min=1, max=20))
    call_permission_password = fields.String(
        validate=Regexp(CALL_PERMISSION_PASSWORD_REGEX), allow_none=True
    )
    subscription_type = fields.Integer(validate=Range(min=0, max=10))
    created_at = fields.DateTime(dump_only=True)
    enabled = StrictBoolean()
    tenant_uuid = fields.String(dump_only=True)
    links = ListLink(Link('users'))

    agent = Nested('AgentSchema', only=['id', 'number', 'links'], dump_only=True)
    call_permissions = Nested(
        'CallPermissionSchema', only=['id', 'name', 'links'], many=True, dump_only=True
    )
    call_pickup_user_targets_flat = Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )

    fallbacks = Nested('UserFallbackSchema', dump_only=True)
    groups = Nested(
        'GroupSchema', only=['uuid', 'id', 'name', 'links'], many=True, dump_only=True
    )
    incalls = Nested(
        'IncallSchema', only=['id', 'extensions', 'links'], many=True, dump_only=True
    )
    lines = Nested(
        'LineListSchema',
        only=[
            'id',
            'name',
            'endpoint_sip',
            'endpoint_sccp',
            'endpoint_custom',
            'extensions',
            'links',
        ],
        many=True,
        dump_only=True,
    )
    forwards = Nested('ForwardsSchema', dump_only=True)
    schedules = Nested(
        'ScheduleSchema', only=['id', 'name', 'links'], many=True, dump_only=True
    )
    services = Nested('ServicesSchema', dump_only=True)
    switchboards = Nested(
        'SwitchboardSchema', only=['uuid', 'name', 'links'], many=True, dump_only=True
    )
    voicemail = Nested('VoicemailSchema', only=['id', 'name', 'links'], dump_only=True)
    queues = Nested(
        'QueueSchema', only=['id', 'name', 'label', 'links'], many=True, dump_only=True
    )
    func_key_template_id = fields.Integer(allow_none=True)

    @pre_dump
    def flatten_call_pickup_targets(self, data, **kwargs):
        if self.only and 'call_pickup_target_users' not in self.only:
            return data

        all_ = [
            list(data.users_from_call_pickup_group_interceptors_user_targets),
            list(data.users_from_call_pickup_group_interceptors_group_targets),
            list(data.users_from_call_pickup_user_targets),
            list(data.users_from_call_pickup_group_targets),
        ]
        data.call_pickup_user_targets_flat = list(set(self._flatten(all_)))

        return data

    @post_dump
    def format_call_pickup_targets(self, data, **kwargs):
        if not self.only or 'call_pickup_target_users' in self.only:
            call_pickup_user_targets = data.pop('call_pickup_user_targets_flat', [])
            data['call_pickup_target_users'] = call_pickup_user_targets
        return data

    @classmethod
    def _flatten(cls, iterable_of_iterable):
        for item in iterable_of_iterable:
            try:
                itercheck = iter(item)
                yield from cls._flatten(itercheck)
            except TypeError:
                yield item

    # DEPRECATED 20.01
    @validates_schema
    def validate_schema(self, data, **kwargs):
        call_record_any_enabled = any(
            (
                data.get('call_record_outgoing_external_enabled') is not None,
                data.get('call_record_outgoing_internal_enabled') is not None,
                data.get('call_record_incoming_external_enabled') is not None,
                data.get('call_record_incoming_internal_enabled') is not None,
            )
        )
        deprecated_call_record_enabled = data.get('call_record_enabled') is not None
        if deprecated_call_record_enabled and call_record_any_enabled:
            raise ValidationError(
                "'call_record_enabled' is deprecated and incompatible with 'call_record_*_enabled' options"
            )

    # DEPRECATED 20.01
    @post_dump
    def dump_call_record_enable_deprecated(self, data, **kwargs):
        if self.only and 'call_record_enabled' not in self.only:
            return data

        call_record_all_enabled = all(
            (
                data.get('call_record_outgoing_external_enabled'),
                data.get('call_record_outgoing_internal_enabled'),
                data.get('call_record_incoming_external_enabled'),
                data.get('call_record_incoming_internal_enabled'),
            )
        )
        data['call_record_enabled'] = call_record_all_enabled
        return data

    # DEPRECATED 20.01
    @post_load
    def load_call_record_enable_deprecated(self, data, **kwargs):
        call_record_enabled = data.pop('call_record_enabled', None)
        if call_record_enabled is None:
            return data

        if call_record_enabled:
            data['call_record_outgoing_external_enabled'] = True
            data['call_record_outgoing_internal_enabled'] = True
            data['call_record_incoming_external_enabled'] = True
            data['call_record_incoming_internal_enabled'] = True
        else:
            data['call_record_outgoing_external_enabled'] = False
            data['call_record_outgoing_internal_enabled'] = False
            data['call_record_incoming_external_enabled'] = False
            data['call_record_incoming_internal_enabled'] = False
        return data


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
    protocol = fields.String()
    enabled = StrictBoolean()


class UserSchemaNullable(UserSchema):
    def on_bind_field(self, field_name, field_obj):
        super().on_bind_field(field_name, field_obj)
        nullable_fields = [
            'call_record_enabled',
            'call_transfer_enabled',
            'caller_id',
            'dtmf_hangup_enabled',
            'enabled',
            'online_call_record_enabled',
            'ring_seconds',
            'simultaneous_calls',
            'supervision_enabled',
        ]
        if field_name in nullable_fields:
            field_obj.allow_none = True


class UserListItemSchema(UserSchemaNullable):
    auth = Nested('WazoAuthUserSchema')
    lines = Nested('UserLineSchema', many=True)
    incalls = Nested('UserIncallSchema', many=True)
    groups = Nested('UserGroupSchema', many=True)
    switchboards = Nested('UserSwitchboardSchema', many=True)
    voicemail = Nested('UserVoicemailSchema', allow_none=True)
    agent = Nested('UserAgentSchema')
    device_id = fields.String(validate=Length(max=255))

    @pre_load
    def init_agent(self, data, **kwargs):

        agent = data.get('agent')

        # if agent exists (even if empty), its missing fields are "auto-populated"
        if agent is not None:
            if 'firstname' not in agent or not agent['firstname']:
                agent['firstname'] = data.get('firstname')
            if 'lastname' not in agent or not agent['lastname']:
                agent['lastname'] = data.get('lastname')
            if 'number' not in agent or not agent['number']:
                agent['number'] = (
                    data.get('lines', [{}])[0].get('extensions', [{}])[0].get('exten')
                )

        return data

    @pre_load
    def init_auth(self, data, **kwargs):
        auth = data.get('auth')
        # if auth exists (even if empty), missing fields are auto-populated
        if auth is not None:
            if 'firstname' not in auth or not auth['firstname']:
                auth['firstname'] = data.get('firstname')
            if 'lastname' not in auth or not auth['lastname']:
                auth['lastname'] = data.get('lastname')
            if 'username' not in auth or not auth['username']:
                auth['username'] = data.get('username')
            if 'password' not in auth or not auth['password']:
                auth['password'] = data.get('password')
            if 'email_address' not in auth or not auth['email_address']:
                auth['email_address'] = data.get('email')
        return data


class UserIncallSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    greeting_sound = fields.String(validate=Length(max=255), allow_none=True)
    caller_id_mode = fields.String(
        validate=OneOf(['prepend', 'overwrite', 'append']), allow_none=True
    )
    caller_id_name = fields.String(validate=Length(max=80), allow_none=True)
    description = fields.String(allow_none=True)
    extensions = Nested(
        'UserExtensionSchema',
        many=True,
    )
    links = ListLink(Link('incalls'))


class UserExtensionSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    exten = fields.String(validate=Length(max=40), required=True)
    context = fields.String(required=True)
    links = ListLink(Link('extensions'))


class UserGroupSchema(BaseSchema):
    uuid = fields.String(validate=Length(max=40), required=True)
    links = ListLink(Link('groups', field='uuid'))


class UserSwitchboardSchema(BaseSchema):
    uuid = fields.String(validate=Length(max=40), required=True)
    links = ListLink(Link('switchboards', field='uuid'))


class UserAgentSchema(AgentSchema):
    number = fields.String(validate=Regexp(NUMBER_REGEX))


class UserLineSchema(LineSchema):
    device_id = fields.String()
