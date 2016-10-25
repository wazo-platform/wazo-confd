# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from marshmallow import Schema, fields, pre_dump, post_load, post_dump
from marshmallow.validate import Length, OneOf, Regexp, Predicate

from xivo_confd.helpers.mallow import StrictBoolean

COMMAND_REGEX = r'^(?!(try)?system\()[a-zA-Z]{3,}\((.*)\)$'
CONTEXT_REGEX = r'^[a-zA-Z0-9_-]{1,39}$'
EXTEN_REGEX = r'^[0-9*#]{1,255}$'


class BaseDestinationSchema(Schema):
    type = fields.String(validate=OneOf(['application',
                                         'conference',
                                         'custom',
                                         'extension',
                                         'group',
                                         'hangup',
                                         'ivr',
                                         'none',
                                         'outcall',
                                         'queue',
                                         'sound',
                                         'user',
                                         'voicemail']),
                         required=True)

    @post_dump
    def convert_type_to_user(self, data):
        if data['type'] == 'endcall':
            data['type'] = 'hangup'
        elif data['type'] == 'meetme':
            data['type'] = 'conference'
        return data

    @post_load
    def convert_type_to_database(self, data):
        if data['type'] == 'hangup':
            data['type'] = 'endcall'
        elif data['type'] == 'conference':
            data['type'] = 'meetme'
        return data


class ApplicationDestinationSchema(BaseDestinationSchema):
    application = fields.String(validate=OneOf(['callback_disa',
                                                'directory',
                                                'disa',
                                                'fax_to_mail',
                                                'voicemail']),
                                attribute='subtype',
                                required=True)

    @post_dump
    def convert_application_to_user(self, data):
        if data['application'] == 'callbackdisa':
            data['application'] = 'callback_disa'
        elif data['application'] == 'faxtomail':
            data['application'] = 'fax_to_mail'
        elif data['application'] == 'voicemailmain':
            data['application'] = 'voicemail'
        return data

    @post_load
    def convert_application_to_database(self, data):
        if data['subtype'] == 'callback_disa':
            data['subtype'] = 'callbackdisa'
        elif data['subtype'] == 'fax_to_mail':
            data['subtype'] = 'faxtomail'
        elif data['subtype'] == 'voicemail':
            data['subtype'] = 'voicemailmain'
        return data


class CallBackDISADestinationSchema(ApplicationDestinationSchema):
    pin = fields.String(validate=(Predicate('isdigit'), Length(max=40)),
                        allow_none=True,
                        attribute='actionarg1')

    context = fields.String(validate=Regexp(CONTEXT_REGEX),
                            attribute='actionarg2', required=True)


class DISADestinationSchema(ApplicationDestinationSchema):
    pin = fields.String(validate=(Predicate('isdigit'), Length(max=40)),
                        allow_none=True,
                        attribute='actionarg1')
    context = fields.String(validate=Regexp(CONTEXT_REGEX),
                            attribute='actionarg2', required=True)


class DirectoryDestinationSchema(ApplicationDestinationSchema):
    context = fields.String(validate=Regexp(CONTEXT_REGEX),
                            attribute='actionarg1', required=True)


class FaxToMailDestinationSchema(ApplicationDestinationSchema):
    email = fields.Email(validate=Length(max=80), attribute='actionarg1', required=True)


class VoicemailMainDestinationSchema(ApplicationDestinationSchema):
    context = fields.String(validate=Regexp(CONTEXT_REGEX),
                            attribute='actionarg1', required=True)


class ConferenceDestinationSchema(BaseDestinationSchema):
    conference_id = fields.Integer(attribute='actionarg1', required=True)


class CustomDestinationSchema(BaseDestinationSchema):
    command = fields.String(validate=(Regexp(COMMAND_REGEX), Length(max=255)),
                            attribute='actionarg1', required=True)


class ExtensionDestinationSchema(BaseDestinationSchema):
    exten = fields.String(validate=Regexp(CONTEXT_REGEX),
                          attribute='actionarg1', required=True)
    context = fields.String(validate=Regexp(CONTEXT_REGEX),
                            attribute='actionarg2', required=True)


class GroupDestinationSchema(BaseDestinationSchema):
    group_id = fields.Integer(attribute='actionarg1', required=True)
    ring_time = fields.Float(attribute='actionarg2', allow_none=True)


class HangupDestinationSchema(BaseDestinationSchema):
    cause = fields.String(validate=OneOf(['busy',
                                          'congestion',
                                          'normal']),
                          attribute='subtype',
                          missing='normal',
                          required=True)

    @post_dump
    def convert_cause_to_user(self, data):
        if data['cause'] == 'hangup':
            data['cause'] = 'normal'
        return data

    @post_load
    def convert_cause_to_database(self, data):
        if data['subtype'] == 'normal':
            data['subtype'] = 'hangup'
        return data


class BusyDestinationSchema(HangupDestinationSchema):
    timeout = fields.Float(attribute='actionarg1', allow_none=True)


class CongestionDestinationSchema(HangupDestinationSchema):
    timeout = fields.Float(attribute='actionarg1', allow_none=True)


class IVRDestinationSchema(BaseDestinationSchema):
    ivr_id = fields.Integer(attribute='actionarg1', required=True)


class NormalDestinationSchema(HangupDestinationSchema):
    pass


class NoneDestinationSchema(BaseDestinationSchema):
    pass


class OutcallDestinationSchema(BaseDestinationSchema):
    outcall_id = fields.Integer(attribute='actionarg1', required=True)
    exten = fields.String(validate=(Predicate('isdigit'), Length(max=255)),
                          attribute='actionarg2',
                          required=True)


class QueueDestinationSchema(BaseDestinationSchema):
    queue_id = fields.Integer(attribute='actionarg1', required=True)
    ring_time = fields.Float(attribute='actionarg2', allow_none=True)


class SoundDestinationSchema(BaseDestinationSchema):
    filename = fields.String(validate=Length(max=255), attribute='actionarg1', required=True)
    skip = StrictBoolean()
    no_answer = StrictBoolean()

    @pre_dump
    def separate_action(self, data):
        options = data.actionarg2 if data.actionarg2 else ''
        data.skip = True if 'skip' in options else False
        data.no_answer = True if 'noanswer' in options else False
        return data

    @post_load
    def merge_action(self, data):
        data['actionarg2'] = '{skip}{noanswer}'.format(
            skip='skip' if data.pop('skip', False) else '',
            noanswer='noanswer' if data.pop('no_answer', False) else ''
        )
        return data


class UserDestinationSchema(BaseDestinationSchema):
    user_id = fields.Integer(attribute='actionarg1', required=True)
    ring_time = fields.Float(attribute='actionarg2', allow_none=True)


class VoicemailDestinationSchema(BaseDestinationSchema):
    voicemail_id = fields.Integer(attribute='actionarg1', required=True)
    skip_instructions = StrictBoolean()
    greeting = fields.String(validate=OneOf(['busy', 'unavailable']), allow_none=True)

    @pre_dump
    def separate_action(self, data):
        options = data.actionarg2 if data.actionarg2 else ''
        data.skip_instructions = True if 's' in options else False
        data.greeting = 'busy' if 'b' in options else 'unavailable' if 'u' in options else None
        return data

    @post_load
    def merge_action(self, data):
        greeting = data.pop('greeting', None)
        data['actionarg2'] = '{}{}'.format(
            'b' if greeting == 'busy' else 'u' if greeting == 'unavailable' else '',
            's' if data.pop('skip_instructions', False) else ''
        )
        return data


class DestinationField(fields.Nested):

    application_schemas = {
        'callback_disa': CallBackDISADestinationSchema,
        'callbackdisa': CallBackDISADestinationSchema,
        'directory': DirectoryDestinationSchema,
        'disa': DISADestinationSchema,
        'fax_to_mail': FaxToMailDestinationSchema,
        'faxtomail': FaxToMailDestinationSchema,
        'voicemail': VoicemailMainDestinationSchema,
        'voicemailmain': VoicemailMainDestinationSchema,
    }

    hangup_schemas = {
        'busy': BusyDestinationSchema,
        'congestion': CongestionDestinationSchema,
        'normal': NormalDestinationSchema,
        'hangup': NormalDestinationSchema,
    }

    destination_schemas = {
        'application': ApplicationDestinationSchema,
        'conference': ConferenceDestinationSchema,
        'meetme': ConferenceDestinationSchema,
        'custom': CustomDestinationSchema,
        'extension': ExtensionDestinationSchema,
        'group': GroupDestinationSchema,
        'hangup': HangupDestinationSchema,
        'endcall': HangupDestinationSchema,
        'ivr': IVRDestinationSchema,
        'none': NoneDestinationSchema,
        'outcall': OutcallDestinationSchema,
        'queue': QueueDestinationSchema,
        'sound': SoundDestinationSchema,
        'user': UserDestinationSchema,
        'voicemail': VoicemailDestinationSchema,
    }

    def __init__(self, **kwargs):
        super(DestinationField, self).__init__(BaseDestinationSchema, **kwargs)

    def _deserialize(self, value, attr, data):
        self.schema.context = self.context
        base = super(DestinationField, self)._deserialize(value, attr, data)
        schema = self.destination_schemas[base['type']]

        if base['type'] == 'application':
            base = fields.Nested(schema)._deserialize(value, attr, data)
            schema = self.application_schemas[base['subtype']]

        if base['type'] == 'endcall':
            base = fields.Nested(schema)._deserialize(value, attr, data)
            schema = self.hangup_schemas[base['subtype']]

        return fields.Nested(schema)._deserialize(value, attr, data)

    def _serialize(self, nested_obj, attr, obj):
        base = super(DestinationField, self)._serialize(nested_obj, attr, obj)
        if not base:
            return base
        schema = self.destination_schemas[base['type']]

        if base['type'] == 'application':
            base = fields.Nested(schema)._serialize(nested_obj, attr, obj)
            schema = self.application_schemas[base['application']]

        if base['type'] == 'hangup':
            base = fields.Nested(schema)._serialize(nested_obj, attr, obj)
            schema = self.hangup_schemas[base['cause']]

        return fields.Nested(schema)._serialize(nested_obj, attr, obj)
